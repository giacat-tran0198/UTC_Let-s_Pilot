import React, { useEffect, useState } from 'react';
import { Link, useHistory } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import Banner from '../utils/Banner';
import { signInUser } from '../../actions/user.action';
import { tokenIsEmpty, tokenIsValid } from '../../utils/utils';

const SignIn = () => {
  const history = useHistory();
  const userStates = useSelector((state) => state.userReducer);
  const dispatch = useDispatch();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  // Handling case when user already have logged in
  useEffect(() => {
    if (!tokenIsEmpty() && tokenIsValid()) history.push('/home');
  }, [history, userStates.token]);

  const handleSignIn = (event) => {
    event.preventDefault();
    dispatch(signInUser(email, password));
  };

  return (
    <div className='signin-page'>
      <Banner title='Sign in into your account' />
      <form className='signin-form-container' onSubmit={handleSignIn}>
        <input
          type='email'
          autoComplete='email'
          placeholder='email'
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type='password'
          autoComplete='current-password'
          placeholder='password'
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button>Log In</button>
        <p className='signin-form-infobox'>{userStates.signInError}</p>
      </form>
      <div className='signin-form-bottom-link'>
        <Link to='/signin/forgot-password'>Forgot password?</Link>
        <Link to='/signup'>Create an account</Link>
      </div>
    </div>
  );
};

export default SignIn;
