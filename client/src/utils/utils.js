import axios from 'axios';

/**
 * Check if a variable is empty or not
 * @param {any} value 
 * @returns {boolean}
 */
export const isEmpty = (value) => {
  return (
    value === undefined ||
    value === null ||
    (typeof value === 'object' && Object.keys(value).length === 0) ||
    (typeof value === 'string' && value.trim().length === 0)
  );
};

/**
 * Check if a message contain a url
 * @param {string} message 
 * @returns  {boolean}
 */
export const checkUrl = (message) => {
  if (isEmpty(message)) return false;

  const regexp = new RegExp(
    /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/,
    'g'
  );

  if (!regexp.test(message)) return false;

  return true;
};

/**
 * Extract all url from a message in a array
 * @param {string} message 
 * @returns {String[]}
 */
export const extractUrl = (message) => {
  if (isEmpty(message)) return null;

  return message.match(
    new RegExp(
      /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_+.~#?&//=]*)/,
      'g'
    )
  );
};

/**
 * Add anchor tag around all links in the message
 * @param {string} message 
 * @returns {string}
 */
export const addAnchorTag = (message) => {
  if (!checkUrl(message)) return message;

  const links = extractUrl(message);

  links.forEach((link) => {
    const position = message.search(link);
    message =
      message.slice(0, position) +
      `<a href='${link}' target='_blank' rel='nofollow, noreferrer, noopener'>` +
      message.slice(position, position + link.length) +
      `</a>` +
      message.slice(position + link.length);
  });

  return message;
};

/**
 * Check if there is a token or not
 * @returns {boolean}
 */
export const tokenIsEmpty = () =>
  isEmpty(localStorage.getItem('token')) ||
  isEmpty(localStorage.getItem('tokenExpiration')) ||
  localStorage.length === 0;

/**
 * Check if the token is valid
 * @returns {boolean}
 */
export const tokenIsValid = () => {
  if (
    !(
      localStorage.getItem('tokenExpiration') - 5 >
      Math.floor(Date.now() / 1000)
    )
  )
    return false;
  else return true;
};

/**
 * Check with the filename if the file is an image
 * @param {string} fileName 
 * @returns {boolean}
 */
export const fileIsImage = (fileName) => {
  const regExp = /\.jpg$|\.jpeg$|\.png$|\.gif$/g;
  if (fileName.match(regExp)) return true;
  return false;
};

/**
 * Check if the password is correct
 * @param {string} password 
 * @returns {boolean}
 */
export const passwordIsValid = (password) => {
  //8 character at least, 1 uppercase, 1 lowercase, 1 digit
  const passwordRegExp = new RegExp(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~]{8,}$/
  );
  return passwordRegExp.test(password);
};

/**
 * Check if the email is correct
 * @param {string} email 
 * @returns {boolean}
 */
export const emailIsValid = (email) => {
  const emailRegExp = new RegExp(
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  );

  return emailRegExp.test(email);
};

/**
 * Check if the client's browser support push notification
 * @returns {boolean}
 */
export const supportPushNotification = () => {
  if (
    'PushManager' in window &&
    'Notification' in window &&
    'serviceWorker' in navigator
  )
    return true;
  else return false;
};

/**
 * Check if the user is already subscribe to push notification service
 * @returns {boolean}
 */
export const alreadySubscribeToPushNotification = async () => {
  if (supportPushNotification()) {
    const swRegistration = await navigator.serviceWorker.ready;
    const pushSubscription = await swRegistration.pushManager.getSubscription();
    if (pushSubscription === null) return false;
    else return true;
  } else return false;
};

/**
 * Subscribe the user to push notification service
 * @returns {void}
 */
export const subscribeToPushNotification = async () => {
  try {
    const swRegistration = await navigator.serviceWorker.ready;

    const responseFetchingPublicKey = await axios({
      method: 'GET',
      url: `api/v1/users/subscription`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });

    const publicKey = responseFetchingPublicKey.data.public_key;
    const pushManagerSubscription = await swRegistration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: publicKey,
    });

    await axios({
      method: 'POST',
      url: `api/v1/users/subscription`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      data: {
        ...JSON.parse(JSON.stringify(pushManagerSubscription)),
        expirationTime: isEmpty(pushManagerSubscription.expirationTime)
          ? 0
          : pushManagerSubscription.expirationTime,
      },
    });
    return true;
  } catch (err) {
    const swRegistration = await navigator.serviceWorker.ready;
    const pushManagerSubscription =
      await swRegistration.pushManager.getSubscription();
    await pushManagerSubscription.unsubscribe();
    console.error(`Error subscribingToPushNotification : ${err}`);
    return false;
  }
};

/**
 * Unsubscribe the user from push notification service
 * @returns {void}
 */
export const unsubscribeFromPushNotification = async () => {
  try {
    const swRegistration = await navigator.serviceWorker.ready;
    const pushManagerSubscription =
      await swRegistration.pushManager.getSubscription();
    if (pushManagerSubscription !== null)
      await pushManagerSubscription.unsubscribe();

    await axios({
      method: 'DELETE',
      url: `api/v1/users/subscription`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return true;
  } catch (err) {
    //console.error(`Error unsubscribingFromPushNotification : ${err}`);
    //Quand même ok si la clef n'est plus enregistré ou si elle n'a pas été supprimé
    return true;
  }
};

/**
 * Check if the user already particip to the meeting
 * @param {number} userId 
 * @param {object} meeting 
 * @returns {boolean}
 */
export const userAlreadyParticipToMeeting = (userId, meeting) => {
  if (isEmpty(userId) || isEmpty(meeting)) return false;

  const participants = [
    meeting.owner,
    ...meeting.coaches,
    ...meeting.participants,
  ];

  if (participants.find((participant) => participant.id === userId))
    return true;
  else return false;
};
