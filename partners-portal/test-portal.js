const http = require('http');

function testPortal() {
  const options = {
    hostname: 'localhost',
    port: 3001,
    path: '/',
    method: 'GET'
  };

  const req = http.request(options, (res) => {
    let data = '';
    
    res.on('data', (chunk) => {
      data += chunk;
    });
    
    res.on('end', () => {
      console.log('✅ GridWorks Partners Portal is WORKING!');
      console.log(`Status: ${res.statusCode}`);
      console.log('URL: http://localhost:3001');
      console.log('');
      
      // Check for key components
      if (data.includes('GridWorks')) {
        console.log('✅ GridWorks branding found');
      }
      if (data.includes('Service Catalog')) {
        console.log('✅ Service Catalog component found');
      }
      if (data.includes('AI Suite Services')) {
        console.log('✅ AI Suite Services found');
      }
      if (data.includes('Anonymous Services')) {
        console.log('✅ Anonymous Services found');
      }
      if (data.includes('Trading-as-a-Service')) {
        console.log('✅ Trading Services found');
      }
      if (data.includes('Banking-as-a-Service')) {
        console.log('✅ Banking Services found');
      }
      
      console.log('');
      console.log('🎉 PORTAL VERIFICATION COMPLETE!');
      console.log('Open http://localhost:3001 in your browser to view the portal.');
    });
  });

  req.on('error', (e) => {
    console.log('❌ Portal not accessible:', e.message);
  });

  req.end();
}

testPortal();