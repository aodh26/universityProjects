let canvas;
let context;

let requestid;
let fpsInterval = 1000 / 30;
let now;
let then = Date.now();

let pretimerelement;
let pretimer = 3;
let time = 30;
let timerelement;

//the ground which moves rather than the player
let ground = {
  x: 50,
  y: -50,
  xchange: 10,
  ychange: 10,
};

//background settup
let tilesperrow = 1;
let tilewidth = 260;
let tileheight = 170;

let background = [
  [0, 0, 0, 0],
  [0, 0, 0, 0],
  [0, 0, 0, 0],
  [0, 0, 0, 0],
];

//chance of a wall appearing
let walls = [];
for (let i = 0; i < 16; i++) {
  walls.push(randint(1, 4));
}
let wall = 10;
let realwallsx = [];
let realwallsy = [];

//player
let player = {
  width: 32,
  height: 48,
  framex: 0,
  framey: 0,
  health: 100,
  score: 0,
};
//bomb settup
let bombs = [];
let bombactive = false;
let bombtimer = -1;
let offsetx = 0;
let offsety = 0;
let bombsound = new Audio("static/bomb.mp4");
let bombimage = new Image();
let explosionimage = new Image();

//score and health display
let scoreelement;
let healthelement;

//sounds
let hitsounds = [
  "static/hit1.mp4",
  "static/hit2.mp4",
  "static/hit3.mp4",
  "static/hit4.mp4",
];
let gameover = new Audio("static/gameover.mp4");
let music = new Audio("static/gamemusicnew.mp3");
//let doorsound = new Audio("static/door.mp4");
//let doorsound2 = new Audio("static/door2.mp4");

//ghost spawns
let enemies = [];
let enemylocations = [130, 910, 80, 590];
let enemyspeeds = [2, 3, 4, 4];
let enemynum = 8;
for (let i = 0; i < enemynum; i += 1) {
  let e = {
    x: enemylocations[randint(0, 1)], //randint(10, 240) * randint(1, 4), //so they dont spawn in a wall
    y: enemylocations[randint(2, 3)], //randint(10, 150) * randint(1, 4),
    width: 32,
    height: 48,
    framex: 0,
    framey: 0,
    speed: enemyspeeds[randint(0, 3)],
  };
  enemies.push(e);
}

//lizard spawns
let lizards = [];
let lizardlocations = [
  [130, 255],
  [910, 255],
  [390, 85],
  [390, 595],
];
let lizardnum = 8;
let bullets = [];
for (let i = 0; i < lizardnum; i += 1) {
  let coordinates = randint(0, 3);
  let l = {
    x: lizardlocations[coordinates][0],
    y: lizardlocations[coordinates][1],
    width: 39,
    height: 48,
    framex: 0,
    framey: 0,
    speed: 5,
  };
  lizards.push(l);
}

//images
let playerimage = new Image();
let flooremptyimage = new Image();
let enemyimage = new Image();
let lizardimage = new Image();

//movement
let moveleft = false;
let moveup = false;
let moveright = false;
let movedown = false;
let shoot = false;

document.addEventListener("DOMContentLoaded", init, false);

let xhttp;

function init() {
  canvas = document.querySelector("canvas");
  context = canvas.getContext("2d");

  load_images([
    "static/player.png",
    "static/floorempty.png",
    "static/ghost.png",
    "static/lizard.png",
    "static/bomb.png",
    "static/explosion.png",
  ]);
  playerimage.src = "static/player.png";
  flooremptyimage.src = "static/floorempty.png";
  enemyimage.src = "static/ghost.png";
  lizardimage.src = "static/lizard.png";
  bombimage.src = "static/bomb.png";
  explosionimage.src = "static/explosion.png";

  pretimerelement = document.querySelector("#pretimer");
  timerelement = document.querySelector("#timer");
  scoreelement = document.querySelector("#score");
  healthelement = document.querySelector("#health");

  player.x = canvas.width / 2;
  player.y = canvas.height / 2;

  window.addEventListener("keydown", activate, false);
  window.addEventListener("keyup", deactivate, false);

  draw();
}

function draw() {
  music.play();
  requestid = window.requestAnimationFrame(draw);

  let now = Date.now();
  let elapsed = now - then;
  if (elapsed <= fpsInterval) {
    return;
  }
  then = now - (elapsed % fpsInterval);

  nomove();
  //resets ground change speed every time draw is called
  ground.xchange = 10;
  ground.ychange = 10;

  //draw background
  context.clearRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "black";
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = "grey";
  //draw floor
  context.fillRect(ground.x, ground.y, canvas.width, canvas.height);
  for (let r = 0; r < 4; r += 1) {
    for (let c = 0; c < 4; c += 1) {
      let tile = background[r][c];
      let tilerow = Math.floor(tile / tilesperrow);
      let tilecol = Math.floor(tile % tilesperrow);
      context.drawImage(
        flooremptyimage,
        tilerow * tilewidth,
        tilecol * tileheight,
        260,
        170, //where it is in the sprite and its size
        r * tilewidth + ground.x,
        c * tileheight + ground.y,
        260,
        170
      );
    }
  }
  //walls and doors

  //horizontal walls
  for (let y = 1; y < 4; y++) {
    let wally = y * 170 + ground.y;
    for (let x = 1; x < 5; x++) {
      let wallnum = y + x;
      if (walls[wallnum] > 1) {
        context.strokeStyle = "black";
        context.lineWidth = wall;
        context.beginPath();
        context.moveTo(x * 260 - 260 + ground.x, wally);
        context.lineTo(x * 260 + ground.x, wally);
        context.stroke();
        context.fillStyle = "#6A8A99";
        context.fillRect(
          x * 260 - 135 + ground.x,
          wally - 5,
          player.width + 10,
          wall
        );
        //checks for a door
        if (
          player.x >= x * 260 - 130 + ground.x - 10 &&
          player.x <= x * 260 - 130 + ground.x + player.width &&
          player.y <= wally + 10 &&
          player.y >= wally - player.height - 10
        ) {
          ground.xchange = 0;
          let doorsound = new Audio("static/door.mp4");
          if (movedown || moveup) {
            doorsound.play();
            player.score += 2;
          }
        }
        //adds only the walls that were drawn
        let w = {
          ytop: wally - player.height - 2,
          ybottom: wally + wall,
          xstart: x * 260 - 260 + ground.x,
          xend: x * 260 + ground.x,
        };
        realwallsx.push(w);
      }
    }
  }
  //checks collision with horizontal walls
  collisionx(realwallsx);

  //vertical walls
  for (let x = 1; x < 4; x++) {
    let wallx = x * 260 + ground.x;
    for (let y = 1; y < 5; y++) {
      let wallnum = y * x;
      if (walls[wallnum] > 2) {
        context.strokeStyle = "black";
        context.lineWidth = wall;
        context.beginPath();
        context.moveTo(wallx, y * 170 - 170 + ground.y);
        context.lineTo(wallx, y * 170 + ground.y);
        context.stroke();
        context.fillStyle = "#6A8A99";
        context.fillRect(
          wallx - 5,
          y * 170 - 85 + ground.y,
          wall,
          player.height + 5
        );
        //checks for a door
        if (
          player.x >= wallx - player.width - 10 &&
          player.x <= wallx + 10 &&
          player.y >= y * 170 + ground.y - 85 - 10 &&
          player.y <= y * 170 + ground.y - 85 + 10 + player.height
        ) {
          ground.ychange = 0;
          let doorsound = new Audio("static/door.mp4");
          if (moveleft || moveright) {
            doorsound.play();
            player.score += 2;
          }
        }
        let w = {
          ytop: y * 170 - 170 + ground.y,
          ybottom: y * 170 + ground.y,
          xstart: wallx - player.width + 2,
          xend: wallx + wall,
        };
        realwallsy.push(w);
      }
    }
  }
  //checks collision with vertical walls
  collisiony(realwallsy);

  //draws lizards
  for (let l of lizards) {
    context.drawImage(
      lizardimage,
      l.width * l.framex,
      l.height * l.framey,
      l.width,
      l.height,
      l.x + ground.x,
      l.y + ground.y,
      l.width,
      l.height
    );
  }

  //draw ghosts
  for (let e of enemies) {
    context.drawImage(
      enemyimage,
      e.width * e.framex,
      e.height * e.framey,
      e.width,
      e.height,
      e.x + ground.x,
      e.y + ground.y,
      e.width,
      e.height
    );
  }
  // respawns ghosts if theyre blown up
  if (enemies.length < enemynum) {
    player.score += enemynum - enemies.length;
    let e = {
      x: enemylocations[randint(0, 1)],
      y: enemylocations[randint(2, 3)],
      width: 32,
      height: 48,
      framex: 0,
      framey: 0,
      speed: enemyspeeds[randint(0, 3)],
    };
    enemies.push(e);
  }
  //draw player
  context.drawImage(
    playerimage,
    player.width * player.framex,
    player.height * player.framey,
    player.width,
    player.height,
    player.x,
    player.y,
    player.width,
    player.height
  );

  //which way the player faces
  if ((moveleft || moveright) && !(moveleft && moveright)) {
    player.framex + 1;
    player.framex = (player.framex + 1) % 4;
  } else if ((moveup || movedown) && !(moveup && movedown)) {
    player.framex + 1;
    player.framex = (player.framex + 1) % 4;
  }

  //placing a bomb
  if (shoot && bombs.length === 0) {
    offsetx = 0;
    offsety = 0;
    let bo = {
      x: player.x,
      y: player.y,
    };
    bombs.push(bo);
    bombactive = true;
    bombtimer = 1;
  }
  //drawing a bomb
  if (bombactive) {
    for (let bo of bombs) {
      context.drawImage(
        bombimage,
        0,
        0,
        20,
        20,
        bo.x + offsetx,
        bo.y + offsety,
        20,
        20
      );
      //bomb exploding
      if (bombtimer === 0) {
        bombsound.play();
        context.drawImage(
          explosionimage,
          0,
          0,
          100,
          100,
          bo.x + offsetx - 50,
          bo.y + offsety - 50,
          100,
          100
        );
      }
    }
  }

  //moves player and bomb accordingly
  if (moveright) {
    ground.x -= ground.xchange;
    offsetx -= ground.xchange;
    player.framey = 2;
  }
  if (moveup) {
    ground.y += ground.ychange;
    offsety += ground.ychange;
    player.framey = 3;
  }
  if (movedown) {
    ground.y -= ground.ychange;
    offsety -= ground.ychange;
    player.framey = 0;
  }
  if (moveleft) {
    ground.x += ground.xchange;
    offsetx += ground.xchange;
    player.framey = 1;
  }

  //collisions with frame
  if (ground.x <= -canvas.width / 2 + player.width) {
    ground.x = -canvas.width / 2 + player.width;
  } else if (ground.x >= canvas.width / 2) {
    ground.x = canvas.width / 2;
  }
  if (ground.y <= -canvas.height / 2 + player.height) {
    ground.y = -canvas.height / 2 + player.height;
  } else if (ground.y >= canvas.height / 2) {
    ground.y = canvas.height / 2;
  }

  //activates enemies if the game has started
  if (pretimer < 0) {
    enemystuff();
    lizardstuff();
  }
  //ends game if player loses all their health
  if (player.health <= 0) {
    stopg(player.score);
  }
  //displays time, score and health
  timerelement.innerHTML = time;
  scoreelement.innerHTML = player.score;
  healthelement.innerHTML = player.health;
}

//key press checker
function activate(event) {
  let key = event.key;
  if (key === "a" || key === "ArrowLeft") {
    moveleft = true;
  } else if (key === "w" || key === "ArrowUp") {
    moveup = true;
  } else if (key === "d" || key === "ArrowRight") {
    moveright = true;
  } else if (key === "s" || key === "ArrowDown") {
    movedown = true;
  } else if (key === " ") {
    shoot = true;
  }
}

//key stop pressing checker
function deactivate(event) {
  let key = event.key;
  if (key === "a" || key === "ArrowLeft") {
    moveleft = false;
  } else if (key === "w" || key === "ArrowUp") {
    moveup = false;
  } else if (key === "d" || key === "ArrowRight") {
    moveright = false;
  } else if (key === "s" || key === "ArrowDown") {
    movedown = false;
  } else if (key === " ") {
    shoot = false;
  }
}

function enemystuff() {
  //which way ghost faces and walks
  for (let e of enemies) {
    if (player.y - ground.y - e.y > 1) {
      e.framey = 0;
      e.y += e.speed;
    } else if (player.y - ground.y - e.y <= 1) {
      e.framey = 3;
      e.y -= e.speed;
    }
    if (player.x - ground.x - e.x >= 0) {
      e.framey = 2;
      e.x += e.speed;
    } else if (player.x - ground.x - e.x < 0) {
      e.framey = 1;
      e.x -= e.speed;
    }
    e.framex + 1;
    e.framex = (e.framex + 1) % 4;

    //checks if a ghost has been blown up
    if (bombactive && bombtimer === 0) {
      for (let bo of bombs) {
        if (
          ((bo.x + offsetx - ground.x - e.x) ** 2 +
            (bo.y + offsety - ground.y - e.y) ** 2) **
            (1 / 2) <
          90
        ) {
          enemies.splice(enemies.indexOf(e), 1);
        }
      }
    }
    //hurting player
    if (
      e.x + ground.x - 15 <= player.x &&
      e.x + ground.x + e.width - 15 >= player.x &&
      player.y === e.y + ground.y
    ) {
      ground.x -= 20;
      player.health -= 25;
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    } else if (
      e.x + ground.x + 15 >= player.x &&
      e.x + ground.x + 15 <= player.x + player.width &&
      player.y === e.y + ground.y
    ) {
      ground.x += 20;
      player.health -= 25;
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    } else if (
      e.y + ground.y - 8 <= player.y &&
      e.y + ground.y + e.height - 8 >= player.y &&
      player.x === e.x + ground.x
    ) {
      ground.y -= 20;
      player.health -= 25;
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    } else if (
      e.y + ground.y + 10 >= player.y &&
      e.y + ground.y + 10 <= player.y + player.height &&
      player.x === e.x + ground.x
    ) {
      ground.y += 20;
      player.health -= 25;
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    }
  }
}

//player wall collision
function collisionx(realwallsx) {
  for (let w of realwallsx) {
    //if players feet touch the wall
    if (
      player.y === w.ytop &&
      ((w.xstart < player.x && player.x < w.xstart + 120) ||
        (w.xend - 110 < player.x && player.x < w.xend))
    ) {
      context.fillStyle = "red";
      context.fillRect(player.x, player.y, 30, 30);
      die();
    }
    if (
      //if players head touches the wall
      player.y === w.ybottom - 10 &&
      ((w.xstart < player.x && player.x < w.xstart + 120) ||
        (w.xend - 115 < player.x && player.x < w.xend))
    ) {
      context.fillStyle = "red";
      context.fillRect(player.x, player.y, 30, 30);
      die();
    }
  }
}

function collisiony(realwallsy) {
  for (let w of realwallsy) {
    //if player touches the wall on the left
    if (
      player.x === w.xstart &&
      ((w.ytop < player.y && player.y < w.ytop + 80) ||
        (w.ybottom - 80 < player.y && player.y < w.ybottom))
    ) {
      context.fillStyle = "red";
      context.fillRect(player.x, player.y, 30, 30);
      die();
    }
    if (
      //if player touches the wall on the right
      player.x === w.xend - 10 &&
      ((w.ytop < player.y && player.y < w.ytop + 80) ||
        (w.ybottom - 80 < player.y && player.y < w.ybottom))
    ) {
      context.fillStyle = "red";
      context.fillRect(player.x, player.y, 30, 30);
      die();
    }
  }
}

function die() {
  player.health = 0;
  gameover.play();
}

//stops game when player dies and displays score
function stopg(score) {
  time = 0;
  window.removeEventListener("keydown", activate, false);
  window.removeEventListener("keyup", deactivate, false);
  window.cancelAnimationFrame(requestid);

  let data = new FormData();
  data.append("score", score);

  xhttp = new XMLHttpRequest();
  xhttp.addEventListener("readystatechange", handleresponse, false);
  xhttp.open("POST", "/~aog2/cgi-bin/ca2/run.py/scoreboard", true);
  xhttp.send(data);
}

function handleresponse() {
  //check that the response has fully arrived
  if (xhttp.readyState === 4) {
    //check the request was successful
    if (xhttp.status === 200) {
      if (xhttp.responseText === "success") {
        getscoreboard();
        //score was successfully stored in database
      } else {
        //score was not successfully stored in database
      }
    }
  }
}

function getscoreboard() {
  if (player.health <= 0) {
    window.open("getscoreboard", "_parent", true);
  }
}

//function for generating a random number
function randint(min, max) {
  return Math.round(Math.random() * (max - min)) + min;
}

//controls the timer adn before game countdown
setInterval(function timer() {
  if (pretimer > 0) {
    pretimerelement.innerHTML = pretimer;
    pretimer -= 1;
  } else if (pretimer === 0) {
    pretimerelement.innerHTML = "Go!";
  }
  if (pretimer < 0) {
    if (time > 0) {
      time -= 1;
    }

    if (time === 0) {
      die();
      timerelement.innerHTML = "times up!";
    }
  }
}, 1000);

//stops the countdown to begin the game
setTimeout(function endpretimer() {
  if (pretimer === 0) {
    pretimerelement.innerHTML = "";
    pretimer -= 1;
  }
}, 5000);

//stops player moving if game hasn't started
function nomove() {
  if (pretimer >= 0) {
    moveup = false;
    movedown = false;
    moveleft = false;
    moveright = false;
    shoot = false;
  }
}

async function load_images(urls) {
  let promises = [];
  for (let url of urls) {
    promises.push(
      new Promise((resolve) => {
        let img = new Image();
        img.onload = resolve;
        img.src = url;
      })
    );
  }
  await Promise.all(promises);
}

//bomb timer
setInterval(function bombtimerf() {
  if (bombactive && bombtimer > 0) {
    bombtimer -= 1;
  } else if (bombactive && bombtimer === 0) {
    bombs.splice(bombs.indexOf(0), 1);
    bombactive = false;
    bombtimer -= 1;
  }
}, 1000);

//controls all things for the lizard enemy
function lizardstuff() {
  //which way the lizard faces and moves
  for (let l of lizards) {
    if (l.framey === 0 && l.y != 595) {
      l.y += l.speed;
    } else if (l.framey === 1 && l.x != 130) {
      l.x -= l.speed;
    } else if (l.framey === 2 && l.x != 910) {
      l.x += l.speed;
    } else if (l.framey === 3 && l.y != 85) {
      l.y -= l.speed;
    }
    //changing direction
    if (l.x % 130 === 0 && l.x % 260 != 0 && l.y % 85 === 0 && l.y % 170 != 0) {
      l.framey = changedirection(l.framey);
    }
    l.framex + 1;
    l.framex = (l.framex + 1) % 4;

    //collision with player
    if (
      l.x + ground.x - 5 <= player.x + player.width - 2 &&
      l.x + ground.x - 5 >= player.x - 2 &&
      player.y === l.y + ground.y
    ) {
      die();
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    } else if (
      l.x + ground.x + l.width - 4 >= player.x &&
      l.x + ground.x + l.width - 4 <= player.x + player.width - 2 &&
      player.y === l.y + ground.y
    ) {
      die();
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    } else if (
      l.y + ground.y - 8 <= player.y &&
      l.y + ground.y + l.height - 8 >= player.y &&
      player.x === l.x + ground.x
    ) {
      die();
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    } else if (
      l.y + ground.y + 10 >= player.y &&
      l.y + ground.y + 10 <= player.y + player.height &&
      player.x === l.x + ground.x
    ) {
      die();
      let hitsound = new Audio(hitsounds[randint(0, 3)]);
      hitsound.play();
    }
  }
}

//makes the lizard less likely to walk back the way it came
function changedirection(framey) {
  //let chance = [framey, randint(0, 3)];
  let newframe = randint(0, 3);
  if (framey + newframe === 3) {
    newframe = changedirection(framey);
  }
  return newframe;
}
