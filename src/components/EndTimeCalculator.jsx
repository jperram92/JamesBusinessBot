import React, { useState, useEffect } from 'react';
import './EndTimeCalculator.css';

const EndTimeCalculator = ({ startTime, duration, onEndTimeChange }) => {
  const [endTime, setEndTime] = useState('');
  const [error, setError] = useState('');

  // Calculate end time when start time or duration changes
  useEffect(() => {
    console.log('EndTimeCalculator useEffect triggered with:', { startTime, duration });
    
    if (startTime && duration) {
      try {
        // Parse the time input (format: HH:mm)
        const [hours, minutes] = startTime.split(':').map(Number);
        console.log('Parsed time:', { hours, minutes });
        
        // Parse duration (e.g., "1 hour" or "30 minutes")
        const durationMatch = duration.match(/(\d+)\s*(hour|hours|minute|minutes)/i);
        console.log('Duration match:', durationMatch);
        
        if (durationMatch) {
          const durationValue = parseInt(durationMatch[1]);
          const durationUnit = durationMatch[2].toLowerCase();
          console.log('Parsed duration:', { durationValue, durationUnit });
          
          // Create date objects for start and end times
          const startDate = new Date();
          startDate.setHours(hours);
          startDate.setMinutes(minutes);
          console.log('Start date:', startDate);
          
          const endDate = new Date(startDate);
          
          // Add duration to end date
          if (durationUnit.startsWith('hour')) {
            endDate.setHours(endDate.getHours() + durationValue);
          } else {
            endDate.setMinutes(endDate.getMinutes() + durationValue);
          }
          console.log('End date:', endDate);
          
          // Format end time in 12-hour format
          const formattedEndTime = endDate.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
          });
          
          console.log('Setting end time to:', formattedEndTime);
          setEndTime(formattedEndTime);
          setError('');
          
          // Notify parent component
          if (onEndTimeChange) {
            console.log('Notifying parent component with end time:', formattedEndTime);
            onEndTimeChange(formattedEndTime);
          }
        } else {
          console.log('Invalid duration format');
          setError('Invalid duration format. Use "1 hour" or "30 minutes"');
          setEndTime('');
        }
      } catch (error) {
        console.error('Error calculating end time:', error);
        setError('Error calculating end time');
        setEndTime('');
      }
    } else {
      console.log('Missing start time or duration');
      setEndTime('');
    }
  }, [startTime, duration, onEndTimeChange]);

  return (
    <div className="end-time-calculator">
      {endTime && (
        <div className="end-time-display">
          <strong>End Time:</strong> {endTime}
        </div>
      )}
      {error && (
        <div className="end-time-error">
          {error}
        </div>
      )}
    </div>
  );
};

export default EndTimeCalculator; 