import React from 'react';

const MeetingElement = ({ meeting, active }) => {

  return (
    <div
      className={
        active ? 'meetingElement-container active' : 'meetingElement-container'
      }
    >
      <p>{meeting.title}</p>
    </div>
  );
};

export default MeetingElement;
