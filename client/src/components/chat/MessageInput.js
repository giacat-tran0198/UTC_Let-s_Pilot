import React, { useState } from 'react';
import { FiPaperclip } from 'react-icons/fi';
import { IoAdd, IoSend } from 'react-icons/io5';
import { TiDeleteOutline } from 'react-icons/ti';
import { useDispatch, useSelector } from 'react-redux';
import { isEmpty } from '../../utils/utils';
import { sendMessage, setMessageReceiver } from '../../actions/chat.action';
import preparedMessage from '../../data/preparedMessage.json';

const MessageInput = ({ socket }) => {
  const chatStates = useSelector((state) => state.chatReducer);
  const userStates = useSelector((state) => state.userReducer);
  const dispatch = useDispatch();
  const [height, setHeight] = useState(25);
  const [message, setMessage] = useState('');
  const [file, setFile] = useState(null);

  // Max size = 10Mb
  const MAX_FILE_SIZE = 1 * Math.pow(10,7) ;

    /**
     * Returns the height of the textarea when new lines are inserted
     * @param {number} value 
     * @returns {number}
     */
  function calcHeight(value) {
    const numberOfLineBreaks = (value.match(/\n/g) || []).length;
    if (numberOfLineBreaks > 5) return 25 + 5 * 20 + 0 + 0;
    // min-height + lines x line-height + padding + border
    const newHeight = 25 + numberOfLineBreaks * 20 + 0 + 0;
    setHeight(newHeight);
    return newHeight;
  }

  /**
   * Send a message through socket connection
   */
  const handleSendMessage = () => {
    if (isEmpty(file) && !isEmpty(message)) {
      socket.emit(
        'send_message',
        {
          project_id: chatStates.meeting.id,
          sender_id: userStates.user.id,
          content: message,
          receiver_id: isEmpty(chatStates.messageReceiver)
            ? 0
            : chatStates.messageReceiver.id,
        },
        (data) => dispatch(sendMessage(data))
      );
    } else if (!isEmpty(file) && file[0].size <= MAX_FILE_SIZE) {
      const fileReader = new FileReader();
      fileReader.readAsDataURL(file[0]);
      fileReader.onload = () => {
        if (!isEmpty(fileReader.result))
          socket.emit(
            'send_message',
            {
              project_id: chatStates.meeting.id,
              sender_id: userStates.user.id,
              content: message,
              receiver_id: isEmpty(chatStates.messageReceiver)
                ? 0
                : chatStates.messageReceiver.id,
              file_name: file[0].name,
              file_base64: fileReader.result,
            },
            (data) => dispatch(sendMessage(data))
          );
        else if (!isEmpty(message))
          socket.emit(
            'send_message',
            {
              project_id: chatStates.meeting.id,
              sender_id: userStates.user.id,
              content: message,
              receiver_id: isEmpty(chatStates.messageReceiver)
                ? 0
                : chatStates.messageReceiver.id,
            },
            (data) => dispatch(sendMessage(data))
          );
      };
    }
    setFile(null);
    setMessage('');
    dispatch(setMessageReceiver({}));
  };

  return (
    <div className='messageInput-container'>
      {!isEmpty(chatStates.messageReceiver) && isEmpty(file) && (
        <div className='messageInput-infobox'>
          <p className='messageInput-infobox-message'>
            {`This message will be sent to ${chatStates.messageReceiver.first_name} ${chatStates.messageReceiver.last_name}`}
          </p>
          <IoAdd
            className='messageInput-infobox-logo'
            size='20'
            onClick={() => dispatch(setMessageReceiver(''))}
          />
        </div>
      )}
      {!isEmpty(file) && isEmpty(chatStates.messageReceiver) && (
        <div className='messageInput-infobox'>
          <p className='messageInput-infobox-message'>
            {file[0].size <= MAX_FILE_SIZE ? `Attached file : ${file[0].name}` : `Max file size is 10MB, ${file[0].name} won't be sent`}
          </p>
          <IoAdd
            className='messageInput-infobox-logo'
            size='20'
            onClick={() => setFile(null)}
          />
        </div>
      )}
      {!isEmpty(file) && !isEmpty(chatStates.messageReceiver) && (
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <div className='messageInput-infobox' style={{ borderRadius: '0' }}>
            <p className='messageInput-infobox-message'>
              Attached file : {file[0].name}
            </p>
            <IoAdd
              className='messageInput-infobox-logo'
              size='20'
              onClick={() => setFile(null)}
            />
          </div>
          <div className='messageInput-infobox' style={{ top: '-62px' }}>
            <p className='messageInput-infobox-message'>
              This message will be sent to {`${chatStates.messageReceiver.first_name} ${chatStates.messageReceiver.last_name}`}
            </p>
            <IoAdd
              className='messageInput-infobox-logo'
              size='20'
              onClick={() => dispatch(setMessageReceiver(''))}
            />
          </div>
        </div>
      )}
      {!chatStates.showPreparedMessage ? (
        <>
          <div className='left-logo-container'>
            {isEmpty(file) ? (
              <>
                <label htmlFor='file-input'>
                  <FiPaperclip className='logo' size='30' color='#4F6D7A' />
                </label>
                <input
                  id='file-input'
                  type='file'
                  accept='.txt,.pdf,.png,.jpg,.jpeg,.gif,.doc'
                  style={{ display: 'none' }}
                  onChange={(e) => setFile(e.target.files)}
                />
              </>
            ) : (
              <TiDeleteOutline
                size='30'
                color='#4F6D7A'
                className='logo'
                onClick={() => setFile(null)}
              />
            )}
          </div>
          <textarea
            placeholder='write a message...'
            style={{
              height: height + 'px',
            }}
            className='messageInput'
            onKeyUp={(event) => {
              calcHeight(event.target.value);
            }}
            onKeyPress={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                handleSendMessage();
              }
            }}
            onChange={(e) => {
              setMessage(e.target.value);
            }}
            value={message}
          ></textarea>
          <div
            className='right-logo-container'
            onClick={() => handleSendMessage()}
          >
            <IoSend size='30' color='#4F6D7A' className='logo' />
          </div>
        </>
      ) : (
        <div className='prepared-message-container'>
          {preparedMessage.map((message) => (
            <button
              key={message.id}
              className='prepared-message-item'
              onClick={() => {
                if (!isEmpty(chatStates.messageReceiver)) {
                  socket.emit(
                    'send_message',
                    {
                      project_id: chatStates.meeting.id,
                      sender_id: userStates.user.id,
                      content: message.message,
                      receiver_id: isEmpty(chatStates.messageReceiver)
                        ? 0
                        : chatStates.messageReceiver.id,
                    },
                    (data) => dispatch(sendMessage(data))
                  );
                  dispatch(setMessageReceiver({}));
                }
              }}
            >
              {message.message}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

export default MessageInput;
