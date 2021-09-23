import React, { useEffect } from 'react';
import { IoAdd } from 'react-icons/io5';
import { useDispatch, useSelector } from 'react-redux';
import { showAddParticipant } from '../../actions/chat.action';
import ParticipantItem from './ParticipantItem';

const ParticipantList = () => {
  const chatStates = useSelector((state) => state.chatReducer);
  const dispatch = useDispatch();

  // Allow the user to click and scroll the participant list
  useEffect(() => {
    let isDown = false;
    let startX = null;
    let scrollLeft = null;

    const setIsDown = (statut) => (isDown = statut);

    const mouseDownHandler = (e) => {
      startX = e.pageX - participantList.offsetLeft;
      scrollLeft = participantList.scrollLeft;
      setIsDown(true);
    };

    const mouseMoveHandler = (e) => {
      if (!isDown) return;
      e.preventDefault();
      const x = e.pageX - participantList.offsetLeft;
      const walk = x - startX; //scroll-fast
      participantList.scrollLeft = scrollLeft - walk;
    };

    const participantList = document.querySelector('.chat-participant-list');
    participantList.addEventListener('mousedown', (e) => mouseDownHandler(e));
    participantList.addEventListener('mouseleave', () => setIsDown(false));
    participantList.addEventListener('mouseup', () => setIsDown(false));
    participantList.addEventListener('mousemove', (e) => mouseMoveHandler(e));

    return () => {
      participantList.removeEventListener('mousemove', mouseMoveHandler);
      participantList.removeEventListener('mouseup', setIsDown);
      participantList.removeEventListener('mouseleave', setIsDown);
      participantList.removeEventListener('mousedown', mouseDownHandler);
    };
  },[]);

  return (
    <div className='chat-participant-list'>
      <div className='chat-participant-item ' id='add-logo'>
        <IoAdd
          style={{ height: '5rem', width: 'auto' }}
          color='#4f6d7a'
          className='chat-participant-item-add-logo'
          onClick={() => dispatch(showAddParticipant())}
        />
      </div>
      <ParticipantItem
        key={chatStates.meeting.owner.id}
        user={chatStates.meeting.owner}
        isCoach={true}
        isOwner={true}
      />
      {chatStates.meeting.coaches.map((coach) => (
        <ParticipantItem key={coach.id} user={coach} isCoach={true} />
      ))}
      {chatStates.meeting.participants.map((participant) => (
        <ParticipantItem
          key={participant.id}
          user={participant}
          isCoach={false}
        />
      ))}
    </div>
  );
};

export default ParticipantList;
