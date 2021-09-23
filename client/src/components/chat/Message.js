import React from 'react';
import parser from 'html-react-parser';
import { addAnchorTag, fileIsImage, isEmpty } from '../../utils/utils';

const Message = ({ message, position }) => {
  return (
    <div
      className='message-item'
      style={
        position === 'right'
          ? { flexDirection: 'row-reverse' }
          : { flexDirection: 'row' }
      }
    >
      {position === 'left' && (
        <img
          className='message-sender-pic'
          src={message.sender.ava ? message.sender.ava : '../image/avatar.svg'}
          alt='profil pic'
        />
      )}
      <div
        className='message-bubble'
        style={
          position === 'left'
            ? {
                backgroundColor: '#4F6D7A',
                color: '#dbe9ee',
                borderRadius: '15px 15px 15px 0px',
              }
            : {
                backgroundColor: '#4F6D7A',
                color: '#dbe9ee',
                borderRadius: '15px 15px 0px 15px',
              }
        }
      >
        {position === 'left' && (
          <p className='message-sender'>{`${message.sender.first_name} ${message.sender.last_name}`}</p>
        )}
        {!isEmpty(message.content) && (
          <p className='message-content'>
            {parser(addAnchorTag(message.content))}
          </p>
        )}
        {!isEmpty(message.file_name) && !fileIsImage(message.file_name) && (
          <>
            <a
              className='attached-file'
              href={message.file_base64}
              download={message.file_name}
            >
              Click to download attached file :
            </a>
            <a
              href={message.file_base64}
              download={message.file_name}
              className='message-image-container'
            >
              <img
                className='attached-file-image'
                src={'./image/fileToDownload.png'}
                alt='attached file'
              />
            </a>
            <a
              className='attached-file'
              href={message.file_base64}
              download={message.file_name}
              style={{
                textAlign: 'center',
                marginTop: '0rem',
                textDecoration: 'none',
                fontStyle: 'normal',
                fontSize: '1rem',
                marginBottom: '1rem',
              }}
            >
              {message.file_name}
            </a>
          </>
        )}
        {!isEmpty(message.file_name) && fileIsImage(message.file_name) && (
          <a
            href={message.file_base64}
            download={message.file_name}
            className='message-image-container'
          >
            <img
              src={message.file_base64}
              alt='message pic'
              className='message-image'
            />
          </a>
        )}
        <p
          className='message-receiver'
          style={
            position === 'right'
              ? { textAlign: 'right' }
              : { textAlign: 'left' }
          }
        >
          {isEmpty(message.receiver)
            ? `For everyone`
            : position === 'left'
            ? `For you`
            : `For ${message.receiver.first_name} ${message.receiver.last_name}`}
        </p>
      </div>
    </div>
  );
};

export default Message;
