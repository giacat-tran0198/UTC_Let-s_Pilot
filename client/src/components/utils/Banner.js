import React from 'react';

const Banner = ({title}) => {
  return (
    <div className='banner'>
      <img  src='/image/banner.svg' alt='two persons out of computer speaking' style={{width:'60vw', maxHeight:'30vh'}} />
      <h1>{title}</h1>
    </div>
  );
};

export default Banner;