#! /usr/bin/env python
# -*- encoding: UTF-8 -*-

import sys
import time
import argparse
import qi
from naoqi import ALModule
from naoqi import ALBroker

class SoundReceiverModule(ALModule):
    """
        TODO
    """

    def __init__( self, strName, args):
        ALModule.__init__( self, strName )

        self.audioDevice = session.service("ALAudioDevice")

        print "Init done"
    
    def startRecording(self):
        print "Start listening ..."
        self.audioDevice.subscribe(self.getName())

        time.sleep(5)

        self.audioDevice.unsubscribe(self.getName())
        print "Stop listening"

    def processRemote(self, nbOfChannels, nbrOfSamplesByChannel, buffer, timeStamp):
        """
            process(const int & nbOfChannels, const int & nbrOfSamplesByChannel, const AL_SOUND_FORMAT * buffer, const ALValue & timeStamp)
        """
        print "Processing"

        print "nbOfChannels: " + str(nbOfChannels)
        print "nbrOfSamplesByChannel: " + str(nbrOfSamplesByChannel)
        print "buffer: " + str(buffer)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", type=str, default="127.0.0.1",
                        help="Robot IP address. On robot or Local Naoqi: use '127.0.0.1'.")
    parser.add_argument("--port", type=int, default=9559,
                        help="Naoqi port number")
    
    arguments = parser.parse_args()
    session = qi.Session()
    try:
        session.connect("tcp://" + arguments.ip + ":" + str(arguments.port))
    except RuntimeError:
        print ("Can't connect to Naoqi at ip \"" + arguments.ip + "\" "
               "on port " + str(arguments.port) +".\n"
               "Please check your script arguments. Run with -h option for help.")
        sys.exit(1)
    
    pythonBroker = ALBroker("myBroker", "0.0.0.0", 9600, arguments.ip, arguments.port)

    SoundReceiver = SoundReceiverModule(args)
    SoundReceiver.startRecording()
