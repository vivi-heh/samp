const $ = s => document.querySelector(s), spin = $('#spin'), reveal = $('#reveal'); let opened = 0;
function celebrate() { const box = $('#confetti'); box.replaceChildren(...Array.from({length: 16}, (_, i) => { const bit = document.createElement('i'); bit.textContent = ['✦','♥','✿'][i % 3]; bit.style.setProperty('--x', `${Math.random()*100}%`); bit.style.setProperty('--r', `${Math.random()*140-70}deg`); return bit; })); setTimeout(() => box.replaceChildren(), 1250); }
async function message() {
  spin.disabled = true; spin.classList.add('spinning');
  const res = await fetch('/api/message', {method:'POST'}), data = await res.json();
  if (res.status === 401) return location.reload();
  setTimeout(() => { opened++; $('#stamp').textContent = `✦ ${opened} ${opened === 1 ? 'memory' : 'memories'} opened`; $('#noteText').textContent = data.text; $('#signature').textContent = `— ${data.student}, with gratitude`; $('#counter').textContent = `${data.remaining} ${data.remaining === 1 ? 'note' : 'notes'} left in your deck`; $('#again').hidden = data.remaining !== 0; reveal.classList.remove('pop'); void reveal.offsetWidth; reveal.classList.add('pop'); celebrate(); spin.disabled = false; spin.classList.remove('spinning'); }, 360);
}
spin.onclick = message;
$('#again').onclick = async () => { await fetch('/api/reset', {method:'POST'}); $('#counter').textContent = 'Deck reshuffled — ready again!'; $('#again').hidden = true; };
$('#logout').onclick = async () => { await fetch('/api/logout', {method:'POST'}); location.reload(); };
let score = 0, playing = false;
$('#play').onclick = () => { if (playing) return; playing = true; score = 0; $('#score').textContent = score; $('#star').hidden = false; let left = 12; const clock = setInterval(() => { $('#timer').textContent = `${--left}s`; if (!left) { clearInterval(clock); playing = false; $('#star').hidden = true; $('#timer').textContent = `you caught ${score}!`; } }, 1000); };
$('#star').onclick = () => { score++; $('#score').textContent = score; $('#star').style.transform = `translate(${Math.random()*110-55}px,${Math.random()*44-22}px) rotate(${Math.random()*60-30}deg)`; };
