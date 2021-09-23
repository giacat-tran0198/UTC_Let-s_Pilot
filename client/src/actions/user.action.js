import axios from 'axios';
import { emailIsValid, passwordIsValid } from '../utils/utils';

export const SIGN_UP_USER = 'SIGN_UP_USER';
export const SIGN_IN_USER = 'SIGN_IN_USER';
export const REFRESH_TOKEN = 'REFRESH_TOKEN';
export const DISCONNECT_USER = 'DISCONNECT_USER';
export const GET_USER = 'GET_USER';
export const ACCOUNT_DATA_CHANGE = 'ACCOUNT_DATA_CHANGE';
export const ACCOUNT_PICTURE_CHANGE = 'ACCOUNT_PICTURE_CHANGE';
export const CREATE_MEETING = 'CREATE_MEETING';
export const GET_MEETINGS = 'GET_MEETINGS';
export const REFRESH_MEETINGS = 'REFRESH_MEETINGS';
export const CHANGE_PASSWORD_ERROR = 'CHANGE_PASSWORD_ERROR';

/**
 * Handle user register
 * @param {string} email 
 * @param {string} login 
  @param {string} password 
 * @param {string} repeatPassword 
 * @param {string} firstName 
 * @param {string} lastName 
 * @returns {void}
 */
export const signUpUser = (
  email,
  login,
  password,
  repeatPassword,
  firstName,
  lastName
) => {
  if (process.env.NODE_ENV && process.env.NODE_ENV !== 'development') {
    if (repeatPassword !== password)
      return {
        type: SIGN_UP_USER,
        payload: {
          signUpError: 'Passwords do not match',
        },
      };

    if (!passwordIsValid(password))
      return {
        type: SIGN_UP_USER,
        payload: {
          signUpError:
            'Password must at least contains 8 characters, 1 uppercase, 1 lowercase & 1 digit',
        },
      };

    if (!emailIsValid(email))
      return {
        type: SIGN_UP_USER,
        payload: {
          signUpError: 'Invalid mail address',
        },
      };
  }

  return (dispatch) => {
    axios({
      method: 'POST',
      url: `api/v1/users/`,
      data: {
        email,
        username: login,
        password,
        first_name: firstName,
        last_name: lastName,
      },
    })
      .then((response) => {
        localStorage.clear();
        localStorage.setItem('token', response.data.authorization);
        localStorage.setItem(
          'tokenExpiration',
          Math.floor(Date.now() / 1000) + response.data.token_expires_in
        );
        return dispatch({
          type: SIGN_UP_USER,
          payload: {
            signUpError: 'Account created successfully',
            token: response.data.authorization,
          },
        });
      })
      .catch(() => {
        return dispatch({
          type: SIGN_UP_USER,
          payload: {
            signUpError: 'Login or email already used',
          },
        });
      });
  };
};

/**
 * Handle user sign in
 * @param {string} email
 * @param {string} password
 * @returns {void}
 */
export const signInUser = (email, password) => {
  return (dispatch) =>
    axios({
      method: 'POST',
      url: `auth/login`,
      data: {
        email,
        password,
      },
    })
      .then((response) => {
        localStorage.clear();
        localStorage.setItem('token', response.data.authorization);
        localStorage.setItem(
          'tokenExpiration',
          Math.floor(Date.now() / 1000) + response.data.token_expires_in
        );
        dispatch({
          type: SIGN_IN_USER,
          payload: {
            signInError: 'Logged in successfully',
            token: response.data.authorization,
          },
        });
      })
      .catch(() => {
        dispatch({
          type: SIGN_IN_USER,
          payload: {
            signInError: 'Email or password incorrect',
          },
        });
      });
};

/**
 * Refresh the user's token
 * @returns {void}
 */
export const refreshToken = () => {
  return (dispatch) => {
    axios({
      method: 'GET',
      url: `auth/refresh-token`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((response) => {
        localStorage.clear();
        localStorage.setItem('token', response.data.authorization);
        localStorage.setItem(
          'tokenExpiration',
          Math.floor(Date.now() / 1000) + response.data.token_expires_in
        );
        console.log('refreshing token...');
        dispatch({
          type: REFRESH_TOKEN,
          payload: { token: response.data.authorization },
        });
      })
      .catch((err) => {
        console.error(err);
        localStorage.clear();
      });
  };
};

/**
 * Fetch user's data
 * @returns {void}
 */
export const getUser = () => {
  return (dispatch) => {
    axios({
      method: 'GET',
      url: `api/v1/users/me`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((response) =>
        dispatch({ type: GET_USER, payload: { user: response.data } })
      )
      .catch((err) => console.error(err));
  };
};

/**
 * Disconnect the current user
 * @returns {void}
 */
export const disconnectUser = () => {
  return (dispatch) => {
    axios({
      method: 'DELETE',
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      url: 'api/v1/users/stream',
    })
      .then((response) => {
        console.log('successfully disconnected from SSE');
        axios({
          method: 'GET',
          url: `auth/logout`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        })
          .then((response) => {
            localStorage.clear();
            dispatch({ type: DISCONNECT_USER });
          })
          .catch((err) => console.error(err));
      })
      .catch((err) => console.error(err));
  };
};

/**
 * Change user's firstname & lastname
 * @param {string} login
 * @param {string} firstName
 * @param {string} lastName
 * @param {string} profilPicture Base64 string representing the picture
 * @returns {void}
 */
export const accountDataChange = (
  login,
  firstName,
  lastName,
  profilPicture
) => {
  return (dispatch) =>
    axios({
      method: 'PUT',
      url: `api/v1/users/me`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      data: {
        username: login,
        first_name: firstName,
        last_name: lastName,
        ava: profilPicture ? profilPicture : '',
      },
    })
      .then((response) => {
        dispatch({
          type: ACCOUNT_DATA_CHANGE,
          payload: { firstName, lastName },
        });
        dispatch(refreshMeeting());
      })
      .catch((err) => console.error(err));
};

/**
 * Change user's profile picture
 * @param {string} login
 * @param {string} firstName
 * @param {string} lastName
 * @param {string} profilPicture Base64 string representing the picture
 * @returns {void}
 */
export const accountPictureChange = (
  login,
  firstName,
  lastName,
  profilPicture
) => {
  return (dispatch) =>
    axios({
      method: 'PUT',
      url: `api/v1/users/me`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      data: {
        username: login,
        first_name: firstName,
        last_name: lastName,
        ava: profilPicture ? profilPicture : '',
      },
    })
      .then((response) => {
        dispatch({
          type: ACCOUNT_PICTURE_CHANGE,
          payload: { profilPicture },
        });
        dispatch(refreshMeeting());
      })
      .catch((err) => console.error(err));
};

/**
 * Create a new meeting
 * @param {string} title
 * @returns {void}
 */
export const createMeeting = (title) => {
  return (dispatch) => {
    axios({
      method: 'POST',
      url: `api/v1/projects/`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      data: {
        title,
      },
    })
      .then((response) => {
        return dispatch({
          type: CREATE_MEETING,
          payload: {
            newMeeting: response.data,
            createMeetingError: 'Meeting successfully created',
          },
        });
      })
      .catch((err) => {
        dispatch({
          type: CREATE_MEETING,
          payload: {
            createMeetingError: 'Meeting name already used',
          },
        });
      });
  };
};

/**
 * Fetch all meetings in which user is involved
 * @returns {void}
 */
export const getMeetings = () => {
  return async (dispatch) => {
    try {
      let response = await axios({
        method: 'GET',
        url: `api/v1/projects/`,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      let fetchMore = response.data.has_next;
      let nextLink = response.data.next;
      let meetings = response.data.data;
      while (fetchMore) {
        response = await axios({
          method: 'GET',
          url: `${nextLink}`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        fetchMore = response.data.has_next;
        nextLink = response.data.next;
        meetings = [...meetings, ...response.data.data];
      }
      return dispatch({
        type: GET_MEETINGS,
        payload: { meetings },
      });
    } catch (err) {
      console.error(err);
    }
  };
};

/**
 * Fetch latest meetings data in which user is involved
 * @returns {void}
 */
export const refreshMeeting = () => {
  return async (dispatch) => {
    try {
      let response = await axios({
        method: 'GET',
        url: `api/v1/projects/`,
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      let fetchMore = response.data.has_next;
      let nextLink = response.data.next;
      let meetings = response.data.data;
      while (fetchMore) {
        response = await axios({
          method: 'GET',
          url: `${nextLink}`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        });
        fetchMore = response.data.has_next;
        nextLink = response.data.next;
        meetings = [...meetings, ...response.data.data];
      }
      return dispatch({
        type: REFRESH_MEETINGS,
        payload: { meetings },
      });
    } catch (err) {
      console.error(err);
    }
  };
};

/**
 * Set the message box for ChangePassword page
 * @param {string} errorMessage
 * @returns {void}
 */
export const changePasswordError = (errorMessage) => ({
  type: CHANGE_PASSWORD_ERROR,
  payload: { errorMessage },
});
