const {injectManifest} = require('workbox-build');

const swSrc = './sw.js';
const swDest = 'build/sw.js';
injectManifest({
  swSrc,
  swDest,
  globDirectory: './build',
  globPatterns: [
		'**/*.{js,json,png,svg,ico,jpg,html,txt,css}'
	],    
}).then(({ count, size }) =>
  console.log(
    `Generated ${swDest}, which will precache ${count} files, totaling ${size} bytes.`
  )
);
