import React from 'react';
import { useHistory } from 'react-router';

const HomeHeader = () => {
  const history = useHistory();
  return (
    <div className='HomeHeader-container'>
      <img
        className='HomeHeader-left-logo'
        src='./image/logo512.png'
        alt='logo chat app'
      />
      <p>Your meetings</p>
      <img
        className='HomeHeader-right-logo'
        src='./image/account_logo.png'
        alt='logo account'
        onClick={() => history.push('/account')}
      />
    </div>
  );
};

export default HomeHeader;
