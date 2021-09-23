import axios from 'axios';

export const ARCHIVE_USER = 'ARCHIVE_USER';
export const UNARCHIVE_USER = 'UNARCHIVE_USER';
export const PROMOTE_USER = 'PROMOTE_USER';
export const DEMOTE_USER = 'DEMOTE_USER';
export const ADMIN_ERROR = 'ADMIN_ERROR';

/**
 * Archive a user
 * @param {string} login 
 * @returns {void}
 */
export const archiveUser = (login) => {
  return (dispatch) => {
    axios({
      method: 'GET',
      url: `api/v1/users/?page=1&per_page=50&filter_by=${login}`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((response) => {
        const userToArchive = response.data.data.find(
          (user) => user.username === login
        );

        axios({
          method: 'POST',
          url: `api/v1/users/archive/${userToArchive.id}`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        })
          .then((response) => {
            dispatch({
              type: ARCHIVE_USER,
            });
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User successfully archived' },
            });
          })
          .catch((err) =>
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User already archived' },
            })
          );
      })
      .catch((err) =>
        dispatch({
          type: ADMIN_ERROR,
          payload: { adminError: 'Invalid login' },
        })
      );
  };
};

/**
 * Unarchive a user
 * @param {string} login 
 * @returns {void}
 */
export const unarchiveUser = (login) => {
  return (dispatch) => {
    axios({
      method: 'GET',
      url: `api/v1/users/?page=1&per_page=50&filter_by=${login}`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((response) => {
        const userToUnarchive = response.data.data.find(
          (user) => user.username === login
        );

        axios({
          method: 'DELETE',
          url: `api/v1/users/archive/${userToUnarchive.id}`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        })
          .then((response) => {
            dispatch({
              type: ARCHIVE_USER,
            });
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User successfully unarchived' },
            });
          })
          .catch((err) =>
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User not archived' },
            })
          );
      })
      .catch((err) =>
        dispatch({
          type: ADMIN_ERROR,
          payload: { adminError: 'Invalid login' },
        })
      );
  };
};

/**
 * Promote a user to be an admin
 * @param {string} login 
 * @returns {void}
 */
export const promoteUser = (login) => {
  return (dispatch) => {
    axios({
      method: 'GET',
      url: `api/v1/users/?page=1&per_page=50&filter_by=${login}`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((response) => {
        const userToUnarchive = response.data.data.find(
          (user) => user.username === login
        );

        axios({
          method: 'POST',
          url: `api/v1/users/admin/${userToUnarchive.id}`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        })
          .then((response) => {
            dispatch({
              type: PROMOTE_USER,
            });
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User successfully promoted' },
            });
          })
          .catch((err) =>
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User already promoted' },
            })
          );
      })
      .catch((err) =>
        dispatch({
          type: ADMIN_ERROR,
          payload: { adminError: 'Invalid login' },
        })
      );
  };
};

/**
 * Demote a user from being an admin
 * @param {string} login 
 * @returns {void}
 */
export const demoteUser = (login) => {
  return (dispatch) => {
    axios({
      method: 'GET',
      url: `api/v1/users/?page=1&per_page=50&filter_by=${login}`,
      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then((response) => {
        const userToUnarchive = response.data.data.find(
          (user) => user.username === login
        );
        axios({
          method: 'DELETE',
          url: `api/v1/users/admin/${userToUnarchive.id}`,
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`,
          },
        })
          .then((response) => {
            dispatch({
              type: PROMOTE_USER,
            });
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User successfully demoted' },
            });
          })
          .catch((err) =>
            dispatch({
              type: ADMIN_ERROR,
              payload: { adminError: 'User already demoted' },
            })
          );
      })
      .catch((err) =>
        dispatch({
          type: ADMIN_ERROR,
          payload: { adminError: 'Invalid login' },
        })
      );
  };
};
