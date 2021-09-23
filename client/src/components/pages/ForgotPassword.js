import React, { useEffect, useState } from 'react';
import { Link, useHistory } from 'react-router-dom';
import Banner from '../utils/Banner';
import { tokenIsEmpty, tokenIsValid } from '../../utils/utils';
import axios from 'axios';

const SignIn = () => {
  const history = useHistory();
  const [infoBox, setInfoBox] = useState();
  const [email, setEmail] = useState('');

  // Handling case when user do not have a valid token or a token at all
  useEffect(() => {
    if (!tokenIsEmpty() && tokenIsValid()) history.push('/home');
  }, [history]);

  /**
   * Handle the password reset request to the API
   * @param {object} event
   */
  const forgotPassword = async (event) => {
    event.preventDefault();
    axios({
      method: 'POST',
      url: `api/v1/users/me/forget-password`,
      data: {
        email,
      },
    })
      .then((response) => {
        if (response.status === 200)
          setInfoBox('Password reset, check your mailbox !');
      })
      .catch(() => setInfoBox('Email not valid'));
  };

  return (
    <div className='signin-page'>
      <Banner title='Sign in into your account' />
      <form className='signin-form-container' onSubmit={forgotPassword}>
        <input
          type='text'
          autoComplete='email'
          placeholder='email'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <button>Reset password</button>
        <p className='signin-form-infobox'>{infoBox}</p>
      </form>
      <div className='signin-form-bottom-link'>
        <Link to='/signin'>Sign in into your account</Link>
        <Link to='/signup'>Create an account</Link>
      </div>
    </div>
  );
};

export default SignIn;
