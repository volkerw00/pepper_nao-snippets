# -*- encoding: UTF-8 -*-

"""
  This script gets the signal from the front microphone of Pepper
  Usage: python CustomSpeechToText.py --qi-url=tcp://ROBOT_IP:9559
"""

import qi
import time
import sys
import math
from threading import Lock

@qi.multiThreaded()
class CustomSpeechToTextModule():

  def __init__( self, strName, session):
    self.session = session
    self.name = strName
    self.ALAudioDevice = self.session.service("ALAudioDevice")
    self.isProcessingDone = False
    self.tempBuffer = []
    self.beamformedBuffer = []
    self.beamformingSampleDiff = 7
    self.lock = Lock()
    self.counter = 0

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
    self.isProcessingDone = True;
    self.lock.release()

  def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timestamp, inputBuffer):
    """ This is the callback that receives the audio buffers """
    self.lock.acquire()
    print 'buffer incoming (' + str(nbOfChannels) + ' channels x ' + str(nbOfSamplesByChannel) + ' samples)'
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

    self.lock.release()

if __name__ == '__main__':
  qiapp = qi.Application(sys.argv)
  qiapp.start()
  session = qiapp.session
  customSpeechToText = CustomSpeechToTextModule("CustomSpeechToText", session)
  session.registerService("CustomSpeechToText", customSpeechToText)
  qiapp.run()
