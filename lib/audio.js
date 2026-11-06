export class Pronouncer {
  constructor(onStatus,{sourceTimeoutMs=8000}={}){this.onStatus=onStatus;this.audio=new Audio();this.generation=0;this.timer=null;this.spokenGeneration=-1;this.sourceTimeoutMs=sourceTimeoutMs;}
  voices(){return(globalThis.speechSynthesis?.getVoices()||[]).filter(v=>/^en[-_]/i.test(v.lang)).sort((a,b)=>Number(/en-US/i.test(b.lang))-Number(/en-US/i.test(a.lang)));}
  stop(){this.generation++;clearTimeout(this.timer);this.audio.onplaying=null;this.audio.onended=null;this.audio.onerror=null;this.audio.pause();this.audio.removeAttribute('src');this.audio.load?.();globalThis.speechSynthesis?.cancel();}
  async play(word,settings,slow=false){
    this.stop();const gen=this.generation,rec=word.sourceAudio||word.recording;let started=false;
    if(settings.preferRecordings&&rec){
      this.audio=new Audio();this.audio.crossOrigin='anonymous';this.audio.preload='none';this.audio.src=rec.url;this.audio.playbackRate=slow?.75:1;
      this.onStatus('Loading source recording…');
      this.audio.onplaying=()=>{if(gen===this.generation){started=true;clearTimeout(this.timer);this.onStatus('Playing source recording');}};
      this.audio.onended=()=>{if(gen===this.generation)this.onStatus('Source recording · ready to replay');};
      this.audio.onerror=()=>{if(gen===this.generation)this.speak(word,settings,slow,gen);};
      this.timer=setTimeout(()=>{if(gen===this.generation&&!started)this.speak(word,settings,slow,gen);},this.sourceTimeoutMs);
      try{await this.audio.play();return;}catch{if(gen!==this.generation)return;}
    }
    this.speak(word,settings,slow,gen);
  }
  speak(word,settings,slow,gen){
    // A media error and play() rejection may both fire for the same request.
    if(gen!==this.generation||this.spokenGeneration===gen)return;
    this.spokenGeneration=gen;clearTimeout(this.timer);this.audio.onplaying=null;this.audio.onended=null;this.audio.onerror=null;this.audio.pause();this.audio.removeAttribute('src');this.audio.load?.();
    if(!globalThis.speechSynthesis){this.onStatus('Audio is unavailable. Use the source-study link or practise with a pronouncer.');return;}
    const voices=this.voices(),v=voices.find(v=>v.voiceURI===settings.voice)||voices.find(v=>/natural|premium|enhanced|samantha|google us/i.test(v.name))||voices[0];
    const utter=new SpeechSynthesisUtterance(word.details?.say||word.word);if(v)utter.voice=v;utter.lang=v?.lang||'en-US';utter.rate=Math.max(.4,settings.rate*(slow?.7:1));
    utter.onstart=()=>{if(gen===this.generation)this.onStatus('Playing computer voice');};
    utter.onend=()=>{if(gen===this.generation)this.onStatus('Computer voice · check source study if pronunciation is unclear');};
    utter.onerror=()=>{if(gen===this.generation)this.onStatus('Audio could not play. Reveal the study card or use a pronouncer; you can skip without a wrong answer.');};
    globalThis.speechSynthesis.cancel();globalThis.speechSynthesis.speak(utter);this.onStatus('Computer voice');
  }
}
