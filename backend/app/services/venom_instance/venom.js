const venom = require('venom-bot');
const express = require('express');
const app = express();
const port = 3001;

process.env.CHROME_PATH = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
process.env.PUPPETEER_EXECUTABLE_PATH = process.env.CHROME_PATH;
process.env.PUPPETEER_HEADLESS = 'new';


let clientInstance;

venom
  .create({
    session: 'veloce_ia',
    multidevice: true,
    headless: false,
    browserArgs: [
      '--headless=new',
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-extensions',
      '--disable-gpu',
      '--disable-software-rasterizer'
    ],
    puppeteerOptions: {
      executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
    }
  })
  .then((client) => start(client))
  .catch((err) => console.log('❌ Erro ao iniciar Venom:', err));

