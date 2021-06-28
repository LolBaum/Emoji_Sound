Server.default.reboot;

SynthDef("EmSynth", {arg freq=500, fmfreq=1, pan=0, att=0.1, rel=20, t_trig=0;
	var sig, volsaw, volsin;
	volsaw = freq.linlin(0, 1000, 1, 0.01);
	volsin = freq.linlin(0, 1000, 0.01, 1);
	sig = Saw.ar(freq*Decay2.kr(t_trig, att, rel/4)*SinOsc.kr(fmfreq), Decay2.kr(t_trig, att, rel, volsaw))+
	SinOsc.ar(freq/2*SinOsc.kr(fmfreq*5), 0, Decay2.kr(t_trig, att, rel, volsin));
	sig = Pan2.ar(sig, pan);
	Out.ar(0, sig);
}).add;

a = Synth(\EmSynth);
a.set(\freq, 800);
a.set(\fmfreq, 0.2);
a.set(\pan, 0);
a.set(\t_trig, 1);

// PROGRAM
(

a = Synth(\EmSynth);
b = Synth(\EmSynth);
c = Synth(\EmSynth);
d = Synth(\EmSynth);
e = Synth(\EmSynth);

~synths = [a, b, c, d, e];
~counter = 0; // for indexing the ~synths

// ServerOptions.devices;
// Server.default.options.outDevice_("Built-in Output");
n = NetAddr.new("127.0.0.1", 57120);    // create the NetAddr

f = { arg sent, neg, neut, pos;
	var freq, fmfreq, synth;
	freq = sent.linlin(-0.6, 0.8, 50, 2000);
	fmfreq = neut.linexp(0, 1, 3, 0.01);
	synth = ~synths[~counter%5];
	synth.set(\freq, freq);
	synth.set(\fmfreq, fmfreq);
	synth.set(\pan, 1.0.rand2);
	synth.set(\t_trig, 1);
	~counter = ~counter +1;
};
// create OSC-Listener
o = OSCFunc({ arg msg, time, addr, recvPort;
	var keyword, sent, neg, neut, pos, freq, fmfreq1, fmfreq2, pan;
	// make sure the msg is formatted correctly
	// if ();
	msg.postln;
	keyword = msg[0]; sent = msg[1]; neg = msg[2]; neut = msg[3]; pos = msg[4];
	f.value(sent: sent, neg: neg, neut: neut, pos: pos);
}, '/emoji');
)

o.free;