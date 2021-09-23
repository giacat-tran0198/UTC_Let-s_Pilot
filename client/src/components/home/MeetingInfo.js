import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useHistory } from 'react-router';
import {
  deleteMeeting,
  joinChat,
  leaveMeeting,
  removeParticipant,
} from '../../actions/chat.action';
import AddParticipantPopUp from '../chat/AddParticipantPopUp';

const MeetingInfo = ({ meeting }) => {
  const history = useHistory();
  const userStates = useSelector((state) => state.userReducer);
  const dispatch = useDispatch();
  const [active, setActive] = useState(false);
  const [addParticipant, setAddParticipant] = useState(false);

  const handleJoinChat = () => {
    dispatch(joinChat(meeting));
    history.push('/chat');
  };

  return (
    <div className='meetingInfo-container' onClick={(e) => e.stopPropagation()}>
      <p>Participants list</p>
      <div className='meetingInfo-participant-list'>
        {[...meeting.participants, ...meeting.coaches, meeting.owner]
          .sort((a, b) => {
            if (a.first_name < b.first_name) return -1;
            if (a.first_name > b.first_name) return 1;
            return 0;
          })
          .map((participant) => {
            if (participant.id !== userStates.user.id)
              return (
                <p
                  key={participant.id}
                  onClick={() => {
                    setActive(participant.id);
                  }}
                  style={
                    active === participant.id
                      ? {
                          backgroundColor: '#4F6D7A',
                          color: '#DBE9EE',
                        }
                      : {}
                  }
                >
                  {`${participant.first_name} ${participant.last_name}`}
                </p>
              );
            else return null;
          })}
      </div>
      <div className='meetingInfo-button-container'>
        <button onClick={() => setAddParticipant(!addParticipant)}>
          Add participant
        </button>
        {meeting.owner.id === userStates.user.id && (
          <button
            onClick={() => dispatch(removeParticipant(meeting.id, active))}
          >
            Remove participant
          </button>
        )}
        <button onClick={() => handleJoinChat()}>Join chat</button>
        <button
          className='red-button'
          onClick={
            meeting.owner.id === userStates.user.id
              ? () => dispatch(deleteMeeting(meeting.id))
              : () => dispatch(leaveMeeting(meeting.id))
          }
        >
          {meeting.owner.id === userStates.user.id
            ? 'Delete meeting'
            : 'Quit meeting'}
        </button>
      </div>
      {addParticipant && (
        <AddParticipantPopUp
          meetingId={meeting.id}
          outsideClickAction={() => setAddParticipant(false)}
        />
      )}
    </div>
  );
};

export default MeetingInfo;
