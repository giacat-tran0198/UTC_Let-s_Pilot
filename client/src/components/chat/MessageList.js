import React, { useEffect, useRef, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  fetchMessages,
  fetchMoreMessages,
  scrolledToBottom,
  stopFetchMoreMessage,
} from '../../actions/chat.action';
import { isEmpty } from '../../utils/utils';
import Message from './Message';

const MessageList = () => {
  const chatStates = useSelector((state) => state.chatReducer);
  const userStates = useSelector((state) => state.userReducer);
  const dispatch = useDispatch();
  const messageEnd = useRef(null);
  const [messagFetched, setMessagFetched] = useState(false)

  // Fetching messages and scrolling message list to bottom
  useEffect(() => {
    if (isEmpty(chatStates.messages) && !messagFetched) {
      dispatch(fetchMessages(chatStates.meeting.id));
      setMessagFetched(true);
    }

    if (chatStates.toScroll && !isEmpty(chatStates.messages)) {
      scrollToBottom();
      dispatch(scrolledToBottom());
    }
  }, [chatStates.meeting.id, chatStates.messages, dispatch, chatStates.toScroll, messagFetched]);

  // Fetching more messages, if all messages are not fetched
  useEffect(() => {
    const messageList = document.querySelector('.message-list');
    const loadMore = () => {
      if (
        chatStates.canFetchMoreMessage &&
        chatStates.hasNext?.hasNext &&
        messageList.scrollTop === 0
      ) {
        dispatch(stopFetchMoreMessage());
        dispatch(fetchMoreMessages(chatStates.hasNext?.linkToNext));
      }
    };
    messageList.addEventListener('scroll', loadMore);

    return () => {
      messageList.removeEventListener('scroll', loadMore);
    };
  },[chatStates.canFetchMoreMessage, chatStates.hasNext?.hasNext, chatStates.hasNext?.linkToNext, dispatch]);

  /**
   * Scroll the message list to the bottom
   */
  const scrollToBottom = () => {
    messageEnd.current.scrollIntoView({
      behavior: 'instant',
      block: 'end',
      inline: 'nearest',
    });
  };

  return (
    <div className='message-list'>
      {!isEmpty(chatStates.messages) &&
        chatStates.messages
          .slice()
          .reverse()
          .map((message, index) => (
            <Message
              message={message}
              key={index}
              position={
                message.sender.id === userStates.user.id ? 'right' : 'left'
              }
            />
          ))}
      <div ref={messageEnd} />
    </div>
  );
};

export default MessageList;
