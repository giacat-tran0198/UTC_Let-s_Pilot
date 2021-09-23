import axios from 'axios';
import React, { useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { API_URL } from '.';
import { getUser, refreshMeeting, refreshToken } from './actions/user.action';
import Routes from './components/routes/Routes';
import { isEmpty, tokenIsEmpty, tokenIsValid } from './utils/utils';

const App = () => {
  const userStates = useSelector((state) => state.userReducer);
  const dispatch = useDispatch();
  const SSE = useRef(null);

  useEffect(() => {
    /* ---------- Token handling ---------- */

    // Fetch a fresh token when the user connect for the first time
    // When user connect for the first time token state is empty
    // The old token is still stored in the local storage
    if (!tokenIsEmpty() && tokenIsValid() && isEmpty(userStates.token)) {
      dispatch(refreshToken());
    }

    // setting the next token refresh  after having fetch the new token
    if (!tokenIsEmpty() && tokenIsValid() && !isEmpty(userStates.token)) {
      console.log(
        'Next token in : ',
        Math.ceil(
          Math.max(
            0,
            (localStorage.getItem('tokenExpiration') -
              (Date.now() / 1000 + 60)) *
              1000
          ) / 60000
        ),
        ' minute(s)'
      );
      setTimeout(() => {
        if (!tokenIsEmpty() && tokenIsValid()) dispatch(refreshToken());
      }, Math.floor(Math.max(0, (localStorage.getItem('tokenExpiration') - (Date.now() / 1000 + 120)) * 1000)));
    } else if (!tokenIsValid()) {
      localStorage.clear();
      console.log('no valid token');
    }

    /* ---------- SSE handling ---------- */

    const handleSSE = (displayNotification) => {
      if (isEmpty(SSE.current) && !isEmpty(userStates.token)) {
        SSE.current = new EventSource(
          `${API_URL}/api/v1/users/stream?token=${localStorage.getItem(
            'token'
          )}`
        );

        SSE.current.addEventListener('error', (event) => {
          console.error('Erreur SSE : ', event);
        });

        SSE.current.addEventListener('action_project', (event) => {
          //console.log(JSON.parse(event.data));
          const data = JSON.parse(event.data);

          dispatch(refreshMeeting());

          if (displayNotification)
            new Notification('Tx Chat', {
              body: data.message,
              icon: '../image/logo192.png',
              vibrate: [200, 100, 200],
              renotify: true,
              tag: 'txChatProject',
              badge: '../image/logo72.png',
              lang: 'EN',
            });
        });

        SSE.current.addEventListener('action_message', (event) => {
          //console.log(JSON.parse(event.data));
          const data = JSON.parse(event.data);

          if (displayNotification)
            new Notification('Tx Chat', {
              body: data.message,
              icon: '../image/logo192.png',
              vibrate: [200, 100, 200],
              renotify: true,
              tag: 'txChatMessage',
              badge: '../image/logo72.png',
              lang: 'EN',
            });
        });

        SSE.current.addEventListener('action_user', (event) => {
          //console.log(JSON.parse(event.data));
          const data = JSON.parse(event.data);

          dispatch(getUser());
          //dispatch(refreshToken());
          if (displayNotification)
            new Notification('Tx Chat', {
              body: data.message,
              icon: '../image/logo192.png',
              vibrate: [200, 100, 200],
              renotify: true,
              tag: 'txChatMessage',
              badge: '../image/logo72.png',
              lang: 'EN',
            });
        });
      }
    };

    //Check if the client's browser support notification & calling handleSSE in consequence
    // Doing the check only when a new token is fetched
    if ('Notification' in window) {
      if (
        Notification.permission === 'granted' &&
        !tokenIsEmpty() &&
        tokenIsValid()
      ) {
        // Notifications permission is granted
        handleSSE(true);
      } else if (
        Notification.permission !== 'denied' ||
        Notification.permission === 'default'
      ) {
        // We request permission for notification
        Notification.requestPermission((permission) => {
          if (permission === 'granted' && !tokenIsEmpty() && tokenIsValid()) {
            handleSSE(true);
          } else if (!tokenIsEmpty() && tokenIsValid()) {
            handleSSE(false);
          }
        });
      } else if (!tokenIsEmpty() && tokenIsValid()) {
        // Notification permission is denied
        handleSSE(false);
      }
    }

    // function use to close SSE connection when closing the tab or browser
    window.onbeforeunload = (event) => {
      const e = event || window.event;
      e.preventDefault();
      if (e) {
        e.returnValue = ''; // Legacy method for cross browser support
        if (!isEmpty(SSE.current)) {
          axios({
            method: 'DELETE',
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`,
            },
            url: 'api/v1/users/stream',
          });
          SSE.current.close();
        }
      }
      return ''; // Legacy method for cross browser support
    };

    return () => {
      if (isEmpty(userStates.token) && !isEmpty(SSE.current)) {
        // User is now disconnected
        SSE.current.close();
        SSE.current = null;
      }
    };
  }, [userStates.token, dispatch]);

  return (
    <>
      <Routes />
    </>
  );
};

export default App;
