s.options.device               = "sprawl_SERVER";
s.options.numInputBusChannels  = 2;
s.options.numOutputBusChannels = 2;
s.options.maxLogins            = 4;
s.options.bindAddress          = "0.0.0.0";

s.waitForBoot({
~dur = 6; // duration of the synths
~amp = 0.3; // amplitude of synths

// Synth-Defs
SynthDef("em_synth_1", {arg pan=0, neg=0.3, neut=0.3, pos=0.3, sent=0.3, dur=6, amp=0.5;
	var sig, oenv, env, fmfreq, freq;
	freq = sent.linlin(-0.6, 0.8, 50, 800);
	fmfreq = sent.linlin(-0.6, 0.8, 1, 20);
	oenv = Env.new([0, amp, amp, 0], [neg*dur, neut*dur, pos*dur], 2);
	env = EnvGen.kr(oenv, doneAction: 2);
	sig = Saw.ar(freq**SinOsc.kr(SinOsc.kr(fmfreq*sent)*fmfreq));
	sig = Pan2.ar(sig*env, pan);
	Out.ar(0, sig);
}).add;

SynthDef("em_synth_2", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3, pan=0, dur=6, amp=0.5;
	var sig, oenv, env, freq;
	freq = sent.linlin(-0.6, 0.8, 60, 200);
	oenv = Env.new([0, amp, amp, 0], [neg*dur, neut*dur, pos*dur], 2);
	env = EnvGen.kr(oenv, doneAction: 2);
	sig = Ringz.ar(WhiteNoise.ar(0.2), freq: freq*SinOsc.kr(freq*0.2), mul: 0.1, decaytime: 0.4);
	sig = Pan2.ar(sig*env, pan);
	Out.ar(0, sig);
}).add;

SynthDef("em_synth_3", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3, dur=6, pan=0, amp=0.5;
	var freq, fmfreq, sig, volsaw, volsin, oenv, env;
	freq = sent.linlin(-0.6, 0.8, 50, 800);
	fmfreq = sent.linlin(-0.6, 0.8, 2, 20);
	oenv = Env.new([0, amp, amp, 0], [neg*dur, neut*dur, pos*dur], 2);
	env = EnvGen.kr(oenv, doneAction: 2);
	volsaw = freq.linlin(0, 1000, 1, 0.01);
	volsin = freq.linlin(0, 1000, 0.01, 1);
	sig = Formant.ar(freq*Saw.kr(fmfreq), mul: 3);
	sig = Pan2.ar(sig*env, pan);
	Out.ar(0, sig);
}).add;

SynthDef("em_synth_4", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3, pan=0, dur=6, amp=0.5;
	var sig, oenv, env, freq;
	freq = sent.linlin(-0.6, 0.8, 60, 200);
	oenv = Env.new([0, amp, amp, 0], [neg*dur, neut*dur, pos*dur], 2);
	env = EnvGen.kr(oenv, doneAction: 2);
	sig = LPF.ar(LFDNoise0.ar(mul: 0.2), freq: freq*SinOsc.kr(freq*0.2), mul: freq.linlin(60, 200, 0.005, 0.00005));
	sig = Pan2.ar(sig*env, pan);
	Out.ar(0, sig);
}).add;
s.sync;
"[INFO] added emoji synth-defs".postln;

~synths = [\em_synth_1, \em_synth_2, \em_synth_3, \em_synth_4];

// Function to play synths
f = { arg neg, neut, pos, sent, dur, amp;
	var synth;
	synth = ~synths.choose();
	Synth(synth, [
			neg: neg,
			neut: neut,
			pos: pos,
			sent: sent,
			pan: 1.0.rand2,
			dur: dur,
			amp: amp
		]);
};

// OSC-Listener
o = OSCFunc({ arg msg, time, addr, recvPort;
	var keyword, sent, neg, neut, pos, freq, fmfreq1, fmfreq2, pan;
	keyword = msg[0];
	sent = msg[1];
	neg = msg[2];
	neut = msg[3];
	pos = msg[4];
	f.value(neg: neg,
			neut: neut,
			pos: pos,
			sent: sent,
			dur: ~dur,
			 amp: ~amp);
}, '/emoji');

"[INFO] created osc-listener on path /emoji".postln;
});

// o.free;
