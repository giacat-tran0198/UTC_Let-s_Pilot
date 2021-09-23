import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import QrReader from 'react-qr-reader';
import { addParticipant } from '../../actions/chat.action';
import { isEmpty, userAlreadyParticipToMeeting } from '../../utils/utils';

const AddParticipantPopUp = ({ outsideClickAction, meetingId }) => {
  const dispatch = useDispatch();
  const userStates = useSelector((state) => state.userReducer);
  const [flashQrCode, setFlashQrCode] = useState(false);
  const [addByLogin, setAddByLogin] = useState(false);
  const [login, setLogin] = useState('');
  const [flashedQrCode, setFlashedQrCode] = useState({});

  const handleAddByLogin = () => {
    dispatch(addParticipant(meetingId, login));
    setLogin('');
  };

  return (
    <div className='context-menu-backdrop' onClick={() => outsideClickAction()}>
      {flashQrCode ? (
        <>
          <QrReader
            delay={1000}
            onScan={(data) => {
              if (!isEmpty(data)) {
                const userData = JSON.parse(data);
                //console.log(JSON.parse(data));
                if (
                  !userAlreadyParticipToMeeting(
                    userData.id,
                    userStates.meetings.find(
                      (meeting) => meeting.id === meetingId
                    )
                  )
                ) {
                  dispatch(addParticipant(meetingId, userData.username));
                  setFlashedQrCode(userData);
                } else console.log('User already added...');
              }
            }}
            onError={console.error}
            style={{ width: '50%' }}
            showViewFinder={false}
          />
          <p className='addbylogin-infobox'>
            {!isEmpty(flashedQrCode)
              ? `${flashedQrCode.first_name} ${flashedQrCode.last_name} added`
              : ''}
          </p>
        </>
      ) : (
        <>
          {addByLogin ? (
            <div
              className='addbylogin-modal'
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              <input
                type='text'
                placeholder='login'
                value={login}
                onChange={(e) => setLogin(e.target.value)}
                onKeyPress={(event) => {
                  if (event.key === 'Enter') {
                    event.preventDefault();
                    handleAddByLogin();
                  }
                }}
              />
              <div className='addbylogin-button-container'>
                <button onClick={() => setAddByLogin(!addByLogin)}>
                  Cancel
                </button>
                <button onClick={() => handleAddByLogin()}>Add</button>
              </div>
              <p className='addbylogin-infobox'>{userStates.addByLoginError}</p>
            </div>
          ) : (
            <div
              className='context-menu-button-container'
              onClick={(e) => {
                e.stopPropagation();
              }}
            >
              <button
                className='context-menu-button'
                onClick={() => setFlashQrCode(!flashQrCode)}
              >
                Scan QR Codes
              </button>
              <button
                className='context-menu-button'
                onClick={() => setAddByLogin(!addByLogin)}
              >
                Add by login
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AddParticipantPopUp;
