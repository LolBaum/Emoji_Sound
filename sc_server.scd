s.options.device               = "sprawl_SERVER";
s.options.numInputBusChannels  = 2;
s.options.numOutputBusChannels = 2;
s.options.maxLogins            = 4;
s.options.bindAddress          = "0.0.0.0";

// opening port
// thisProcess.openUDPPort(57110);
// NetAddr.localAddr.postln;
// n = NetAddr.new("127.0.0.1", 57110);

s.boot;

s.waitForBoot({
// Synth-Defs
SynthDef("em_synth_1", {arg pan=0, neg=0.3, neut=0.3, pos=0.3, sent=0.3, dur=15;
	var sig, oenv, env, env_dur, fmfreq, freq;
	freq = sent.linlin(-0.6, 0.8, 50, 800);
	fmfreq = sent.linlin(-0.6, 0.8, 1, 20);
	env_dur = dur/3;
	oenv = Env.new([0, 1, 1, 0], [neg*env_dur, neut*env_dur, pos*env_dur]);
	env = EnvGen.kr(oenv, doneAction: 2);
	sig = Saw.ar(freq**SinOsc.kr(SinOsc.kr(fmfreq*sent)*fmfreq));
	sig = Pan2.ar(sig*env, pan);
	Out.ar(0, sig);
}).add;

SynthDef("em_synth_2", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3, pan=0, dur=20;
	var sig, oenv, env, env_dur, freq;
	freq = sent.linlin(-0.6, 0.8, 60, 200);
	env_dur = dur/3;
	oenv = Env.new([0, 1, 1, 0], [neg*env_dur, neut*env_dur, pos*env_dur]);
	env = EnvGen.kr(oenv, doneAction: 2);
	sig = Ringz.ar(WhiteNoise.ar(0.2), freq: freq*SinOsc.kr(freq*0.2), mul: 0.1, decaytime: 0.4);
	sig = Pan2.ar(Compander.ar(sig*env), pan);
	Out.ar(0, sig);
}).add;

SynthDef("em_synth_3", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3, dur=15, pan=0;
	var freq, fmfreq, sig, volsaw, volsin, oenv, env, env_dur;
	freq = sent.linlin(-0.6, 0.8, 50, 800);
	fmfreq = sent.linlin(-0.6, 0.8, 2, 20);
	env_dur = dur/3;
	oenv = Env.new([0, 1, 1, 0], [neg*env_dur, neut*env_dur, pos*env_dur]);
	env = EnvGen.kr(oenv, doneAction: 2);
	volsaw = freq.linlin(0, 1000, 1, 0.01);
	volsin = freq.linlin(0, 1000, 0.01, 1);
	sig = Formant.ar(freq*Saw.kr(fmfreq), mul: 3);
	sig = Pan2.ar(sig*env, pan);
	Out.ar(0, sig);
}).add;
s.sync;
"Created synth-defs".postln;

// Function to play synths
~synths = [\em_synth_1, \em_synth_2, \em_synth_3];

f = { arg neg, neut, pos, sent;
	var synth;
	synth = ~synths.choose();
	Synth(synth, [neg: neg, neut: neut, pos: pos, sent: sent]);
};

// create OSC-Listener
o = OSCFunc({ arg msg, time, addr, recvPort;
	var keyword, sent, neg, neut, pos, freq, fmfreq1, fmfreq2, pan;
	// make sure the msg is formatted correctly
	// if ();
	msg.postln;
	keyword = msg[0]; sent = msg[1]; neg = msg[2]; neut = msg[3]; pos = msg[4];
	f.value(neg: neg, neut: neut, pos: pos, sent: sent);
}, '/emoji');

});


// o.free;
