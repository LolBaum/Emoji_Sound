SynthDef("FMSynth", {arg freq=500, fmfreq1=1, fmfreq2=0.2, pan=0, att=0.1, rel=10, t_trig=0;
	var sig;
	sig = Saw.ar(freq*SinOsc.kr(fmfreq1*SinOsc.kr(fmfreq2, pi/2), pi/2, Decay2.kr(t_trig, att, rel)*0.3))*
	SinOsc.ar(freq*2*SinOsc.kr(fmfreq1*SinOsc.kr(fmfreq2, pi/2)), 0, Decay2.kr(t_trig, att, rel)*0.3);
	sig = Pan2.ar(sig, pan);
	Out.ar(0, sig);
}).add;

a = Synth(\FMSynth);

a.set(\fmfreq1, 0.2)
a.set(\fmfreq2, 0.5)
a.set(\freq, 100)
a.set(\pan, -1)
a.set(\t_trig, 1);

// PROGRAM
(
~synthFM = Synth(\FMSynth);

// ServerOptions.devices;
// Server.default.options.outDevice_("Built-in Output");
n = NetAddr.new("127.0.0.1", 57120);    // create the NetAddr

f = { arg freq, fmfreq1, fmfreq2, pan;
	~synthFM.set(\freq, freq);
	~synthFM.set(\fmfreq1, fmfreq1);
	~synthFM.set(\fmfreq2, fmfreq2);
	~synthFM.set(\pan, pan);
	~synthFM.set(\t_trig, 1);
};
// create OSC-Listener
o = OSCFunc({ arg msg, time, addr, recvPort;
	var keyword, sent, neg, neut, pos, freq, fmfreq1, fmfreq2, pan;
	// make sure the msg is formatted correctly
	// if ();
	msg.postln;
	keyword = msg[0]; sent = msg[1]; neg = msg[2]; neut = msg[3]; pos = msg[4];
	"This just came in:".post; sent.postln;
	freq = sent.linlin(-1, 1, 100, 400);
	fmfreq1 = neg.linexp(-1, 1, 0.001, 50);
	fmfreq2 = pos.linexp(-1, 1, 0.001, 10);
	pan = sent;
	"path: ".post; keyword.postln;
	"freq: ".post; freq.postln;
	"fmfreq1: ".post; fmfreq1.postln;
	"fmfreq2: ".post; fmfreq2.postln;
	"pan: ".post; pan.postln;
	f.value(freq: freq, fmfreq1: fmfreq1, fmfreq2: fmfreq2, pan: pan);
}, '/emoji');
)

o.free;