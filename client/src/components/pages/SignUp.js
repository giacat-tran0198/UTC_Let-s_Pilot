import React, { useEffect, useState } from 'react';
import { Link, useHistory } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import Banner from '../utils/Banner';
import { signUpUser } from '../../actions/user.action';
import { tokenIsEmpty, tokenIsValid } from '../../utils/utils';

const SignUp = () => {
  const [email, setEmail] = useState('');
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [repeatPassword, setRepeatPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const userStates = useSelector((state) => state.userReducer);
  const dispatch = useDispatch();
  const history = useHistory();

  // Handling case when user already have logged in
  useEffect(() => {
    if (!tokenIsEmpty() && tokenIsValid()) history.push('/home');
  },[history,userStates.token]);

  const handleSignUp = (event) => {
    event.preventDefault();
    dispatch(
      signUpUser(email, login, password, repeatPassword, firstName, lastName)
    );
  };

  return (
    <div className='signin-page'>
      <Banner title='Create your account' />
      <form className='signin-form-container' onSubmit={handleSignUp}>
        <div className='signup-grid-form'>
          <input
            type='email'
            autoComplete='email'
            placeholder='email'
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            type='text'
            autoComplete='username'
            placeholder='login'
            value={login}
            onChange={(e) => setLogin(e.target.value)}
          />
          <input
            type='password'
            autoComplete='new-password'
            placeholder='password'
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <input
            type='password'
            autoComplete='new-password'
            placeholder='repeat-password'
            value={repeatPassword}
            onChange={(e) => setRepeatPassword(e.target.value)}
          />
          <input
            type='text'
            autoComplete='given-name'
            placeholder='first name'
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <input
            type='text'
            autoComplete='family-name'
            placeholder='last name'
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
        </div>
        <button>Create account</button>
        <p className='signin-form-infobox'>{userStates.signUpError}</p>
      </form>
      <p className='signin-form-bottom-link'>
        <Link to='/'>Account already exists ?</Link>
      </p>
    </div>
  );
};

export default SignUp;
