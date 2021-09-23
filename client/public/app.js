if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('./sw.js')
      .then((registration) => {
        console.info(
          `Service worker successfully registered : ${registration.scope}`
        );
      })
      .catch((err) =>
        console.error(`Failed to register service worker :  ${err}`)
      );
  });
}
