// Luzie Ahrens and Laurin Dahm
// 22.09.2021

// SC-script to receive OSC-Messages and create a sound according to the sentiment/localization-information
// incoming OSC-Messages must be in the following format:
// "keyword sentiment negative neutral positive azimuth elevation"

s.options.device               = "sprawl_SERVER";
s.options.numInputBusChannels  = 2;
s.options.numOutputBusChannels = 2;
s.options.maxLogins            = 4;
s.options.bindAddress          = "0.0.0.0";
// RootNode.freeAll;
// RootNode.new(s);

s.waitForBoot({
~dur = 6; // duration of the synths
~amp = 1; // amplitude of synths
~hoa_order      = 1;
~n_hoa_channels = pow(~hoa_order + 1.0 ,2.0).asInteger;


/////////////////////////////////////////////////////////////////////////////////
// Synth Definitions
/////////////////////////////////////////////////////////////////////////////////

// FIRST SYNTH
SynthDef("emoji_1", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3,
		azim=0,
		elev=0,
		out_bus=0;
		var sig, fmfreq, freq, env;

		// Creating signal
		freq = sent.linlin(-0.6, 0.8, 50, 800);
		fmfreq = sent.linlin(-0.6, 0.8, 1, 20);
		sig = Saw.ar(freq**SinOsc.kr(SinOsc.kr(fmfreq*sent)*fmfreq));

		// Envelope
		env = Env.new([0, ~amp, ~amp, 0], [~dur*neg, ~dur*neut, ~dur*pos], 2);
		env = EnvGen.kr(env, doneAction: 2);

		// Binaural Encoder
		sig = HOASphericalHarmonics.coefN3D(~hoa_order, azim, elev) * sig * env;

		Out.ar(out_bus, sig);
}).add;

// SECOND SYNTH
SynthDef("emoji_2", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3,
		azim=0,
		elev=0,
		out_bus=0;
		var sig, env, freq;

		// Creating signal
		freq = sent.linlin(-0.6, 0.8, 60, 200);
		sig = Ringz.ar(WhiteNoise.ar(0.2), freq: freq*SinOsc.kr(freq*0.2),
			mul: 0.1, decaytime: 0.4);

		// Envelope
		env = Env.new([0, ~amp, ~amp, 0], [~dur*neg, ~dur*neut, ~dur*pos], 2);
		env = EnvGen.kr(env, doneAction: 2);

		// Binaural Encoder
		sig = HOASphericalHarmonics.coefN3D(~hoa_order, azim, elev) * sig * env;
		Out.ar(out_bus, sig);
}).add;

// THIRD SYNTH
SynthDef("emoji_3", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3,
		azim=0,
		elev=0,
		out_bus=0;
		var freq, fmfreq, sig, volsaw, volsin, env;

		// Creating signal
		freq = sent.linlin(-0.6, 0.8, 50, 800);
		fmfreq = sent.linlin(-0.6, 0.8, 2, 20);
		volsaw = freq.linlin(0, 1000, 1, 0.01);
		volsin = freq.linlin(0, 1000, 0.01, 1);
		sig = Formant.ar(freq*Saw.kr(fmfreq), mul: 3);

		// Envelope
		env = Env.new([0, ~amp, ~amp, 0], [~dur*neg, ~dur*neut, ~dur*pos], 2);
		env = EnvGen.kr(env, doneAction: 2);

		// Binaural Encoder
		sig = HOASphericalHarmonics.coefN3D(~hoa_order, azim, elev) * sig * env;
		Out.ar(out_bus, sig);
}).add;

// FOURTH SYNTH
SynthDef("emoji_4", {arg neg=0.3, neut=0.3, pos=0.3, sent=0.3,
		azim=0,
		elev=0,
		out_bus=0;
		var sig, env, freq;

		// Creating signal
		freq = sent.linlin(-0.6, 0.8, 60, 200);
		sig = LPF.ar(WhiteNoise.ar(0.2), freq: freq*SinOsc.kr(freq*0.2), mul: 0.05);

		// Envelope
		env = Env.new([0, ~amp, ~amp, 0], [~dur*neg, ~dur*neut, ~dur*pos], 2);
		env = EnvGen.kr(env, doneAction: 2);

		// Binaural Encoder
		sig = HOASphericalHarmonics.coefN3D(~hoa_order, azim, elev) * sig * env;
		Out.ar(out_bus, sig);
}).add;

s.sync;
"[INFO] Added Emoji Synth-Defs".postln;


/////////////////////////////////////////////////////////////////////////////////
//  Binaural Decoder and Ambisonic Bus
/////////////////////////////////////////////////////////////////////////////////

// load HOA stuff for binaural decoder
HOABinaural.loadbinauralIRs(s);

SynthDef(\hoa_binaural_decoder,
	{
		|
		in_bus  = nil, // audio input bus index
		out_bus = nil  // audio output bus index
		|
		var sig = HOABinaural.ar(~hoa_order, In.ar(in_bus,~n_hoa_channels));
		Out.ar(out_bus, sig);
}).add;

s.sync;

"[INFO] Added Binaural Decoder".postln;

// audio bus for the encoded ambisonics signal
~ambi_BUS      = Bus.audio(s, ~n_hoa_channels);

// group for all synths
~synth_GROUP = Group.new(s);

// add one decoder after the synth group
~decoder = Synth.after(~synth_GROUP, \hoa_binaural_decoder,
	[
		\in_bus,  ~ambi_BUS.index,
		\out_bus, 0,
]);

/////////////////////////////////////////////////////////////////////////////////
// OSC-Listener and PLAY-function
/////////////////////////////////////////////////////////////////////////////////

~synths = [\emoji_1, \emoji_2, \emoji_3, \emoji_4];

// Function to PLAY SYNTH
~play = { arg neg, neut, pos, sent, azim=0, elev=0;
	var synth;
	synth = ~synths.choose();
	Synth(synth, [
			neg: neg,
			neut: neut,
			pos: pos,
			sent: sent,
			azim: azim,
			elev: elev,
			out_bus: ~ambi_BUS.index
		],
		target: ~synth_GROUP
		);
};

// OSC-Listener
// incoming OSC-Messages must be in the following format:
// "keyword sentiment negative neutral positive azimuth elevation"
o = OSCFunc({ arg msg, time, addr, recvPort;
	var keyword, sent, neg, neut, pos, azim, elev;
	keyword = msg[0];
	sent = msg[1];
	neg = msg[2];
	neut = msg[3];
	pos = msg[4];
	azim = msg[5];
	elev = msg[6];
	~play.value(neg: neg,
			neut: neut,
			pos: pos,
			sent: sent,
			azim: azim,
			elev: elev
		);
}, '/emoji');

"[INFO] Created OSC-Listener on path /emoji".postln;
});
