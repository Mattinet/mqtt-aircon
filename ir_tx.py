#!/usr/bin/env python

import pigpio

class tx:

   """
   """

   def __init__(self, pi, gpio, carrier_hz):

      """
      Initialises an IR tx on a Pi's gpio with a carrier of
      carrier_hz.
      """

      self.pi = pi
      self.gpio = gpio
      self.carrier_hz = carrier_hz
      self.micros = 1000000 / carrier_hz
      self.on_mics = self.micros / 2
      self.off_mics = self.micros - self.on_mics

      self.wf = []
      self.wid = -1

      pi.set_mode(gpio, pigpio.OUTPUT)

   def clear_code(self):
      self.wf = []
      if self.wid >= 0:
         self.pi.wave_delete(self.wid)

   def send_code(self):
      pulses = self.pi.wave_add_generic(self.wf)
      print("waveform uses {} pulses".format(pulses))
      self.wid = self.pi.wave_create()
      if self.wid >= 0:
         self.pi.wave_send_once(self.wid)
         while self.pi.wave_tx_busy():
            pass

   def add_to_code(self, on, off):

      # add on cycles of carrier
      for x in range(on):
         self.wf.append(pigpio.pulse(1<<self.gpio, 0, self.on_mics))
         self.wf.append(pigpio.pulse(0, 1<<self.gpio, self.off_mics))

      # add off cycles of no carrier
      self.wf.append(pigpio.pulse(0, 0, off * self.micros))

