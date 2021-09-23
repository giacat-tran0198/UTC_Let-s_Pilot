import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { showContextMenu } from '../../actions/chat.action';
import { isEmpty } from '../../utils/utils';

const ParticipantItem = ({ user, isCoach, isOwner }) => {
  const userStates = useSelector((state) => state.userReducer);
  const chatStates = useSelector((state) => state.chatReducer);
  const dispatch = useDispatch();

  /**
   * Handle the action when participant item get clicked
   */
  const handleClick = () => {
    if (
      userStates.user.id === chatStates.meeting.owner.id ||
      chatStates.meeting.coaches.find(
        (coach) => coach.id === userStates.user.id
      )
    )
      dispatch(showContextMenu(user, isCoach));
  };

  return (
    <div className={!isEmpty(chatStates.userConnected.find((userConnected) => userConnected === user.id )) ? 'chat-participant-item user-is-connected' : 'chat-participant-item user-is-not-connected'} onClick={handleClick}>
      <img src={user.ava ? user.ava : '../image/avatar.svg'} alt='profil pic'  />
      <p
        className='chat-participant-item-name'        
        style={
          isCoach && !isOwner
            ? { textDecoration: 'underline' }
            : isOwner
            ? { textDecoration: 'underline', fontStyle: 'italic' }
            : {}
        }
      >{`${user.first_name}`}<br/>{`${user.last_name}`}</p>
    </div>
  );
};

export default ParticipantItem;
