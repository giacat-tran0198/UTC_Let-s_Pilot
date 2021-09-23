import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory } from 'react-router';
import {
  accountDataChange,
  accountPictureChange,
  disconnectUser,
  getUser,
} from '../../actions/user.action';
import {
  alreadySubscribeToPushNotification,
  isEmpty,
  subscribeToPushNotification,
  supportPushNotification,
  tokenIsEmpty,
  tokenIsValid,
  unsubscribeFromPushNotification,
} from '../../utils/utils';
import HeaderWithArrow from '../utils/HeaderWithArrow';

const MyAccount = () => {
  const dispatch = useDispatch();
  const userStates = useSelector((state) => state.userReducer);
  const history = useHistory();
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [isSubscribeToPush, setIsSubscribeToPush] = useState(null);
  const [file, setFile] = useState(null);

  // Max size = 2Mb
  const MAX_FILE_SIZE = 2 * Math.pow(10, 6);

  // Handling case when user do not have a valid token or a token at all
  // Handle fetching user's data
  useEffect(() => {
    if (tokenIsEmpty() || !tokenIsValid()) history.push('/');
    if (isEmpty(userStates.user)) dispatch(getUser());
    else {
      setFirstName(userStates.user.first_name);
      setLastName(userStates.user.last_name);
    }
    const asyncFunction = async () => {
      setIsSubscribeToPush(await alreadySubscribeToPushNotification());
    };
    isSubscribeToPush === null && asyncFunction();
  }, [userStates.user, dispatch, history, isSubscribeToPush]);

  const handleNameChange = () => {
    dispatch(
      accountDataChange(
        userStates.user.username,
        firstName,
        lastName,
        userStates.user.ava
      )
    );
  };

  const handlePictureChange = (e) => {
    if (e.target.id === 'reset') {
      dispatch(
        accountPictureChange(userStates.user.username, firstName, lastName, '')
      );
    } else if (!isEmpty(file)) {
      if (file[0].size <= MAX_FILE_SIZE) {
        const fileReader = new FileReader();
        fileReader.readAsDataURL(file[0]);
        fileReader.onload = () => {
          dispatch(
            accountPictureChange(
              userStates.user.username,
              firstName,
              lastName,
              fileReader.result
            )
          );
        };
      }
    }
  };

  const handleDisconnect = () => {
    dispatch(disconnectUser());
    history.push('/');
  };

  const handlePushSubscription = async () => {
    if (isSubscribeToPush) {
      const success = await unsubscribeFromPushNotification();
      if (success) setIsSubscribeToPush(false);
    } else {
      const success = await subscribeToPushNotification();
      if (success) setIsSubscribeToPush(true);
    }
  };

  /**
   * Action when leftIcon of header is clicked
   */
  const leftIconAction = () => {
    history.push('/home');
  };

  return (
    <>
      <HeaderWithArrow title={'My account'} leftIconAction={leftIconAction} />
      <h1 className='myAccount-header'>Manage your account</h1>
      <div className='account-page'>
        <div className='change-profil-form'>
          {userStates.user.ava ? (
            <img
              className='profile-pic'
              src={userStates.user.ava}
              alt='profile pic'
            />
          ) : (
            <img
              className='profile-pic'
              src='../image/avatar.svg'
              alt='profile pic'
            />
          )}
          <p className='login-info'>{`Your login : ${userStates.user.username}`}</p>

          <div className='change-picture-button'>
            <label htmlFor='change-profil-pic' className='change-picture-label'>
              Select profil picture
            </label>
            <input
              id='change-profil-pic'
              type='file'
              accept='.png,.jpg,.jpeg,.gif'
              style={{ display: 'none' }}
              onChange={(e) => setFile(e.target.files)}
            />
          </div>
          <button
            className='change-picture-button'
            id='reset'
            onClick={handlePictureChange}
          >
            Reset profil picture
          </button>
          <button
            className='change-picture-button'
            onClick={handlePictureChange}
          >
            Apply changes
          </button>
          <p className='signin-form-infobox'>
            {file &&
              file[0].size > MAX_FILE_SIZE &&
              'Max profile picture size is 2MB'}
          </p>
        </div>
        <div className='signin-form-container'>
          <label htmlFor='firstName'>First Name</label>
          <input
            id='firstName'
            type='text'
            required
            placeholder='first name'
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <label htmlFor='lastName'>Last name</label>
          <input
            id='lastName'
            type='text'
            required
            placeholder='last name'
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
          <button onClick={handleNameChange}>Save changes</button>
          <button
            style={{ marginTop: '3rem' }}
            onClick={() => history.push('/account/password')}
          >
            Change password
          </button>
        </div>
      </div>
      <div className='red-button-container'>
        <button
          style={{ marginTop: '3rem' }}
          className='button-style'
          onClick={() => supportPushNotification() && handlePushSubscription()}
        >
          {!supportPushNotification()
            ? `Push notification not supported`
            : isSubscribeToPush
            ? `Unsubscribe from push notification`
            : `Subscribe to push notification`}
        </button>
        <button onClick={handleDisconnect} className='red-button'>
          Discconnect
        </button>
      </div>
    </>
  );
};

export default MyAccount;
