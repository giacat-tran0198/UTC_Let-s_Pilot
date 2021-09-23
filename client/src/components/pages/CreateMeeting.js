import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import Banner from '../utils/Banner';
import HeaderWithArrow from '../utils/HeaderWithArrow';
import { useHistory } from 'react-router';
import { tokenIsEmpty, tokenIsValid } from '../../utils/utils';
import { createMeeting } from '../../actions/user.action';

const CreateMeeting = () => {
  const dispatch = useDispatch();
  const userState = useSelector((state) => state.userReducer);
  const history = useHistory();
  const [meetingName, setMeetingName] = useState('');
  
  // Handling case when user do not have a valid token or a token at all
  useEffect(() => {
    if (tokenIsEmpty() || !tokenIsValid()) history.push('/');
  },[history]);

  const handleCreateMeeting = (e) => {
    e.preventDefault();
    dispatch(createMeeting(meetingName));
    setMeetingName('');
  };

   /**
   * Action when leftIcon of header is clicked
   */
  const leftIconAction = () => {
    history.push('/home');
  };

  return (
    <>
      <HeaderWithArrow
        title={'Create your meeting'}
        leftIconAction={leftIconAction}
      />
      <div className='signin-page'>
        <Banner title='Enter a meeting name' />
        <form className='signin-form-container' onSubmit={handleCreateMeeting}>
          <input
            type='text'
            required
            placeholder='meeting name'
            value={meetingName}
            onChange={(e) => setMeetingName(e.target.value)}
          />

          <button>Create meeting</button>
          <p className='signin-form-infobox'>{userState.createMeetingError}</p>
        </form>
      </div>
    </>
  );
};

export default CreateMeeting;
