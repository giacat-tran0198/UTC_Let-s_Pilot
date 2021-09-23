import React from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  designateCoach,
  removeParticipant,
  removePrivileges,
  setMessageReceiver,
  showContextMenu,
} from '../../actions/chat.action';

const ChatContextMenu = () => {
  const dispatch = useDispatch();
  const chatStates = useSelector((state) => state.chatReducer);

  return (
    <div
      className='context-menu-backdrop'
      onClick={() => dispatch(showContextMenu())}
    >
      <div
        className='context-menu-button-container'
      >
        <button
          className='context-menu-button'
          onClick={() => dispatch(setMessageReceiver(chatStates.targetedUser))}
        >
          Send a private message
        </button>
        {!chatStates.targetedUserIsCoach &&
        chatStates.targetedUser.id !== chatStates.meeting.owner.id ? (
          <button
            className='context-menu-button'
            onClick={() =>
              dispatch(
                designateCoach(chatStates.meeting.id, chatStates.targetedUser)
              )
            }
          >
            Designate coach
          </button>
        ) : (
          chatStates.targetedUser.id !== chatStates.meeting.owner.id && (
            <button
              className='context-menu-button'
              onClick={() =>
                dispatch(
                  removePrivileges(
                    chatStates.meeting.id,
                    chatStates.targetedUser
                  )
                )
              }
            >
              Remove privileges
            </button>
          )
        )}
        {!chatStates.targetedUserIsCoach && (
          <button
            className='context-menu-button'
            onClick={() =>
              dispatch(
                removeParticipant(
                  chatStates.meeting.id,
                  chatStates.targetedUser.id
                )
              )
            }
          >
            Remove participant
          </button>
        )}
      </div>
    </div>
  );
};

export default ChatContextMenu;
