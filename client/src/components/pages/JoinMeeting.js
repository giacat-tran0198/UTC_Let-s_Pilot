import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory } from 'react-router';
import QRCode from 'qrcode.react';
import Banner from '../utils/Banner';
import HeaderWithArrow from '../utils/HeaderWithArrow';
import { isEmpty, tokenIsEmpty, tokenIsValid } from '../../utils/utils';
import { getUser } from '../../actions/user.action';

const JoinMeeting = () => {
  const dispatch = useDispatch();
  const userStates = useSelector((state) => state.userReducer);
  const history = useHistory();

  /**
   * Calculate the max viewWidth of the window
   */
  const viewWidth = Math.max(
    document.documentElement.clientWidth || 0,
    window.innerWidth || 0
  );

  /**
   * Calculate the max viewHeight of the window
   */
  const viewHeight = Math.max(
    document.documentElement.clientHeight || 0,
    window.innerHeight || 0
  );

  // Handling case when user do not have a valid token or a token at all
  // Handle fetching user's data
  useEffect(() => {
    if (tokenIsEmpty() || !tokenIsValid()) history.push('/');
    if (isEmpty(userStates.user)) dispatch(getUser());
  }, [dispatch, history, userStates.user]);

  /**
   * Action when leftIcon of header is clicked
   */
  const handleHeaderArrowClick = () => {
    history.push('/home');
  };

  return (
    <>
      <HeaderWithArrow
        title={'Join a new meeting'}
        leftIconAction={handleHeaderArrowClick}
      />
      <div className='joinMeeting-container'>
        <Banner title='Show your QR code to join a meeting' />
        <QRCode
          className='qrcode'
          value={JSON.stringify({
            id: userStates.user.id,
            username: userStates.user.username,
            email: userStates.user.email,
            first_name: userStates.user.first_name,
            last_name: userStates.user.last_name,
          })}
          size={
            viewWidth * 0.6 > viewHeight * 0.5
              ? viewHeight * 0.5
              : viewWidth * 0.6
          }
          includeMargin={false}
          style={{ margin: '2rem 0 5rem 0' }}
        />
      </div>
    </>
  );
};

export default JoinMeeting;
