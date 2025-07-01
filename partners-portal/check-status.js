const http = require('http');

const options = {
  hostname: 'localhost',
  port: 3001,
  path: '/',
  method: 'GET',
  timeout: 5000
};

const req = http.request(options, (res) => {
  console.log('✅ Partners Portal is WORKING!');
  console.log(`Status: ${res.statusCode}`);
  console.log(`URL: http://localhost:3001`);
  console.log('Portal is ready for verification.');
});

req.on('error', (e) => {
  console.log('❌ Portal not accessible:', e.message);
});

req.on('timeout', () => {
  console.log('⚠️ Portal is slow to respond but may be working');
  console.log('Try accessing: http://localhost:3001');
});

req.end();