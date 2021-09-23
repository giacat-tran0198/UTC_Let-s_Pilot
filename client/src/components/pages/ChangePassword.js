import React, { useEffect, useState } from 'react';
import { useHistory } from 'react-router';
import { useDispatch, useSelector } from 'react-redux';
import Banner from '../utils/Banner';
import HeaderWithArrow from '../utils/HeaderWithArrow';
import axios from 'axios';
import { passwordIsValid, tokenIsEmpty, tokenIsValid } from '../../utils/utils';
import { changePasswordError, getMeetings } from '../../actions/user.action';

const ChangePassword = () => {
  const dispatch = useDispatch();
  const userStates = useSelector((state) => state.userReducer);
  const history = useHistory();
  const [password, setPassword] = useState('');
  const [repeatNewPassword, setRepeatNewPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');

  // Handling case when user do not have a valid token or a token at all
  useEffect(() => {
    if (tokenIsEmpty() || !tokenIsValid()) history.push('/');
  }, [history]);

  /**
   * Handle the password change with the API
   * @param {object} event 
   * @returns {void}
   */
  const handleChangePassword = (event) => {
    event.preventDefault();

    if (repeatNewPassword !== newPassword)
      return dispatch(changePasswordError('Passwords do not match'));

    if (!passwordIsValid(password))
      return dispatch(
        changePasswordError(
          'Password must at least contains 8 characters, 1 uppercase, 1 lowercase & 1 digit'
        )
      );

    axios({
      method: 'PUT',
      url: `api/v1/users/me/reset-password`,

      headers: {
        Authorization: `Bearer ${localStorage.getItem('token')}`,
      },
      data: {
        older_password: password,
        new_password: newPassword,
      },
    })
      .then(() => {
        dispatch(changePasswordError('Password successfully changed'));
        dispatch(getMeetings());
        history.push('/home');
      })
      .catch(() => dispatch(changePasswordError('Wrong password')));
  };

  /**
   * Action when leftIcon of header is clicked
   */
  const leftIconAction = () => {
    history.push('/account');
  };

  return (
    <>
      <HeaderWithArrow title={'My account'} leftIconAction={leftIconAction} />
      <div className='signin-page'>
        <Banner title='Manage your account' />
        <form className='signin-form-container' onSubmit={handleChangePassword}>
          <input
            type='email'
            autoComplete='email'
            value={userStates.user.email}
            readOnly
            hidden
          />
          <input
            type='password'
            required
            placeholder='old password'
            autoComplete='current-password'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type='password'
            required
            placeholder='repeat new password'
            autoComplete='new-password'
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
          />
          <input
            type='password'
            required
            placeholder='new password'
            autoComplete='new-password'
            value={repeatNewPassword}
            onChange={(e) => setRepeatNewPassword(e.target.value)}
          />
          <button>Change password</button>
          <p className='signin-form-infobox'>
            {userStates.changePasswordError}
          </p>
        </form>
      </div>
    </>
  );
};

export default ChangePassword;
