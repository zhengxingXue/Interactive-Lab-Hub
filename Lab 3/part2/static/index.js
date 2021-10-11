// setup clock for current time
let clock = () => {
  let date = new Date();
  let hrs = date.getHours();
  let mins = date.getMinutes();
  let secs = date.getSeconds();
  let period = "AM";
  if (hrs == 0) {
    hrs = 12;
  } else if (hrs >= 12) {
    hrs = hrs - 12;
    period = "PM";
  }
  hrs = hrs < 10 ? "0" + hrs : hrs;
  mins = mins < 10 ? "0" + mins : mins;
  secs = secs < 10 ? "0" + secs : secs;

  let time = `${hrs}:${mins}:${secs} ${period}`;
  document.getElementById("clock").innerText = time;
  setTimeout(clock, 1000);
};
clock();

// setup socket
const socket = io();
socket.on('connect', () => {

});

const mic = document.getElementById('mic');
const start_listen = document.getElementById('start_listen');
const wordsIn = document.getElementById('wordsIn');
const speak = document.getElementById('speak');

// User Status Section 
const user_sleep = document.getElementById('user_sleep');
const user_getup = document.getElementById('user_getup');
const user_jump = document.getElementById('user_jump');
const user_delay_succeeded = document.getElementById('user_delay_succeeded');
const user_delay_failed = document.getElementById('user_delay_failed');

user_sleep.onclick = () => {
  socket.emit('speak', "What doesn’t kill you, simply makes you stranger!")
}

user_getup.onclick = () => {
  socket.emit('speak', "Why so serious?")
}

user_jump.onclick = () => {
  socket.emit('speak', "Let’s put a smile on that face!")
}

user_delay_succeeded.onclick = () => {
  wordsIn.value = "Okay, next alarm at "
  wordsIn.focus()
}

user_delay_failed.onclick = () => {
  wordsIn.value = "Get up, you have plan at "
  wordsIn.focus()
}

// Speak section send button onclick 
speak.onclick = () => {
  socket.emit('speak', wordsIn.value)
  wordsIn.value = ''
}
wordsIn.onkeyup = (e) => { if (e.keyCode === 13) { speak.click(); } };

// listen section start button onclick
const src = mic.src
mic.src = ''

start_listen.onclick = () => {
  if (mic.paused) {
    console.log('redo audio')
    mic.src = src
    mic.play()
    start_listen.innerText = 'end'
  } else {
    mic.pause()
    mic.src = '';
    start_listen.innerText = 'start'
  }
}

// socket disconnect
socket.on('disconnect', () => {
  console.log('disconnect')
  mic.src = ''
});

setInterval(() => {
  socket.emit('ping-gps', 'dat')
}, 100)

var vlSpec = {
  $schema: 'https://vega.github.io/schema/vega-lite/v5.json',
  data: { name: 'table' },
  width: 400,
  mark: 'line',
  encoding: {
    x: { field: 'x', type: 'quantitative', scale: { zero: false } },
    y: { field: 'y', type: 'quantitative' },
    color: { field: 'category', type: 'nominal' }
  }
};
vegaEmbed('#chart', vlSpec).then((res) => {
  let x, y, z;
  let counter = -1;
  let cat = ['x', 'y', 'z']
  let minimumX = -100;
  socket.on('pong-gps', (new_x, new_y, new_z) => {
    counter++;
    minimumX++;
    const newVals = [new_x, new_y, new_z].map((c, v) => {
      return {
        x: counter,
        y: c,
        category: cat[v]
      };
    })
    const changeSet = vega
      .changeset()
      .insert(newVals)
      .remove((t) => {
        return t.x < minimumX;
      });
    res.view.change('table', changeSet).run();
  })

})
