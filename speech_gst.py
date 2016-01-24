# Copyright (C) 2009 Aleksey S. Lim
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst
Gst.init(None)

import speech

def _message_cb(bus, message, pipe):
    if message.type in (Gst.MessageType.EOS, Gst.MessageType.ERROR):
        pipe.set_state(Gst.State.NULL)
        if pipe is play_speaker[1]:
            speech.reset_cb()
    elif message.type == Gst.MessageType.ELEMENT and \
            message.get_structure().get_name() == 'espeak-mark':
        mark = message.get_structure().get_value('mark')
        speech.highlight_cb(int(mark))

def _create_pipe():
    pipe = Gst.Pipeline()

    source = Gst.ElementFactory.make('espeak', 'source')
    pipe.add(source)

    sink = Gst.ElementFactory.make('autoaudiosink', 'sink')
    pipe.add(sink)
    source.link(sink)

    bus = pipe.get_bus()
    bus.add_signal_watch()
    bus.connect('message', _message_cb, pipe)	

    return (source, pipe)

def _speech(speaker, words):
    speaker[0].props.pitch = speech.pitch
    speaker[0].props.rate = speech.rate
    speaker[0].props.voice = speech.voice[1]
    speaker[0].props.text = words;
    speaker[1].set_state(Gst.State.NULL)
    speaker[1].set_state(Gst.State.PLAYING)

info_speaker = _create_pipe()
play_speaker = _create_pipe()
play_speaker[0].props.track = 2

def voices():
    return info_speaker[0].props.voices

def say(words):
    _speech(info_speaker, words)

def play(words):
    _speech(play_speaker, words)

def is_stopped():
    for i in play_speaker[1].get_state(Gst.CLOCK_TIME_NONE):
        if isinstance(i, Gst.State) and i == Gst.State.NULL:
            return True
    return False

def stop():
    play_speaker[1].set_state(Gst.State.NULL)
