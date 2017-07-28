# -*- encoding: UTF-8 -*-

"""
  This script gets the signal from the front microphone of Pepper
  Usage: python CustomSpeechToText.py --qi-url=tcp://ROBOT_IP:9559
"""

import base64
import json
import Queue
import time
import threading
from threading import Lock
import sys

import qi

from ws4py.client.threadedclient import WebSocketClient
import base64, json, ssl, subprocess, threading, time

class SpeechToTextClient(WebSocketClient):
    def __init__(self):
        ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"

        username = "user "
        password = "password"
        auth_string = "%s:%s" % (username, password)
        base64string = base64.encodestring(auth_string).replace("\n", "")

        self.listening = False

        try:
            WebSocketClient.__init__(self, ws_url,
                headers=[("Authorization", "Basic %s" % base64string)])
            self.connect()
        except: print "Failed to open WebSocket."

    def opened(self):
        data = {"action": "start",
                "content-type": "audio/l16;rate=48000",
                "continuous": True,
                "interim_results": True,
                "inactivity_timeout": 600,
                'max_alternatives': 3,
                'timestamps': True,
                'word_confidence': True}
        print("sendMessage(init)")
        # send the initialization parameters
        self.send(json.dumps(data).encode('utf8'))

    def received_message(self, message):
        message = json.loads(str(message))
        if "state" in message:
            if message["state"] == "listening":
                self.listening = True
        print "Message received: " + str(message)

    def close(self):
        self.listening = False
        self.stream_audio_thread.join()
        WebSocketClient.close(self)

@qi.multiThreaded()
class SpeechToTextModule():

  def __init__( self, strName, session, stt_client):
    self.session = session
    self.name = strName
    self.ALAudioDevice = self.session.service("ALAudioDevice")
    self.isProcessingDone = False
    self.tempBuffer = []
    self.beamformedBuffer = []
    self.beamformingSampleDiff = 7
    self.lock = Lock()
    self.counter = 0
    self.stt_client = stt_client

  def startStreaming(self):
    """ Process one speech sentence """
    # ask for all microphones signals interleaved sampled at 48kHz
    self.ALAudioDevice.setClientPreferences(self.name, 48000, 0, 0)
    self.ALAudioDevice.subscribe(self.name)
    while self.isProcessingDone == False:
      time.sleep(0.1)
    self.ALAudioDevice.unsubscribe(self.name)
    self.isProcessingDone = False

  def stopStreaming(self):
    """ Interrupt recognition """
    self.lock.acquire()
    self.isProcessingDone = True
    self.lock.release()

  def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timestamp, inputBuffer):
    """ This is the callback that receives the audio buffers """
    self.lock.acquire()
    # print 'buffer incoming (' + str(nbOfChannels) + ' channels x ' + str(nbOfSamplesByChannel) + ' samples)'
    self.tempBuffer += inputBuffer
    self.beamformedBuffer = []

    if (len(self.tempBuffer) / nbOfChannels) >= self.beamformingSampleDiff:
      nbSamples = len(self.tempBuffer) / nbOfChannels - self.beamformingSampleDiff
      for i in range(nbSamples):
        self.beamformedBuffer += [(
                                self.tempBuffer[i * nbOfChannels] + \
                                self.tempBuffer[i * nbOfChannels + 1] + \
                                self.tempBuffer[(i + self.beamformingSampleDiff) * nbOfChannels + 2] + \
                                self.tempBuffer[(i + self.beamformingSampleDiff) * nbOfChannels + 3]) / nbOfChannels]
      self.tempBuffer = self.tempBuffer[(nbSamples * nbOfChannels):]
      # Send beamformedBuffer to server if supports 48kHz or downsample it to 16kHz.
      self.counter = self.counter + 1
      self.stt_client.send(inputBuffer, binary=True)

    self.lock.release()

if __name__ == '__main__':

  # start recording via qi module
  qiapp = qi.Application(sys.argv)
  qiapp.start()
  session = qiapp.session
  customSpeechToText = SpeechToTextModule("SpeechToText", session, SpeechToTextClient())
  session.registerService("SpeechToText", customSpeechToText)

  qiapp.run()
