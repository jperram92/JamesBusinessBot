import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './ItineraryManager.css';
import EndTimeCalculator from './EndTimeCalculator';

const ItineraryManager = ({ onItineraryUpdate }) => {
  const [rawItinerary, setRawItinerary] = useState('');
  const [processedItinerary, setProcessedItinerary] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recipientEmail, setRecipientEmail] = useState('');
  const [subject, setSubject] = useState('');
  const [additionalRecipients, setAdditionalRecipients] = useState('');
  const [emailSent, setEmailSent] = useState(false);
  
  // New state variables for meeting details
  const [meetingDate, setMeetingDate] = useState('');
  const [meetingTime, setMeetingTime] = useState('');
  const [meetingDuration, setMeetingDuration] = useState('');
  const [meetingLocation, setMeetingLocation] = useState('');
  const [showMeetingDetails, setShowMeetingDetails] = useState(true);
  const [endTime, setEndTime] = useState('');

  // Handle end time change from the EndTimeCalculator component
  const handleEndTimeChange = (newEndTime) => {
    console.log('ItineraryManager received end time:', newEndTime);
    setEndTime(newEndTime);
  };

  // Format time for display
  const formatTime = (timeString) => {
    if (!timeString) return '';
    try {
      const [hours, minutes] = timeString.split(':').map(Number);
      const date = new Date();
      date.setHours(hours);
      date.setMinutes(minutes);
      return date.toLocaleTimeString('en-US', {
        hour: 'numeric',
        minute: '2-digit',
        hour12: true
      });
    } catch (error) {
      console.error('Error formatting time:', error);
      return timeString;
    }
  };

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    setEmailSent(false);

    // Combine meeting details with raw itinerary if provided
    let fullItinerary = rawItinerary;
    
    if (meetingDate || meetingTime || meetingDuration || meetingLocation) {
      const meetingDetails = `Meeting Details:
Date: ${formatDate(meetingDate) || 'To be determined'}
Start Time: ${formatTime(meetingTime) || 'To be determined'}
End Time: ${endTime || 'To be determined'}
Duration: ${meetingDuration || 'To be determined'}
Location/Platform: ${meetingLocation || 'To be determined'}

${rawItinerary}`;
      
      fullItinerary = meetingDetails;
    }

    try {
      const response = await axios.post('/api/process-itinerary', {
        rawItinerary: fullItinerary,
        meetingDetails: {
          date: formatDate(meetingDate),
          startTime: formatTime(meetingTime),
          endTime: endTime,
          duration: meetingDuration,
          location: meetingLocation
        }
      });

      // Make sure we have a valid response with sections
      if (response.data && response.data.sections) {
        setProcessedItinerary(response.data);
        if (onItineraryUpdate) {
          onItineraryUpdate(response.data);
        }
      } else {
        throw new Error('Invalid response format from server');
      }
    } catch (err) {
      setError('Failed to process itinerary. Please try again.');
      console.error('Error processing itinerary:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendEmail = async () => {
    if (!recipientEmail) {
      setError('Please enter a recipient email address');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Combine meeting details with raw itinerary if provided
      let fullItinerary = rawItinerary;
      
      if (meetingDate || meetingTime || meetingDuration || meetingLocation) {
        const meetingDetails = `Meeting Details:
Date: ${formatDate(meetingDate) || 'To be determined'}
Start Time: ${formatTime(meetingTime) || 'To be determined'}
End Time: ${endTime || 'To be determined'}
Duration: ${meetingDuration || 'To be determined'}
Location/Platform: ${meetingLocation || 'To be determined'}

${rawItinerary}`;
        
        fullItinerary = meetingDetails;
      }

      const response = await axios.post('/api/send-itinerary', {
        rawItinerary: fullItinerary,
        recipientEmail,
        subject: subject || 'Meeting Invitation',
        additionalRecipients: additionalRecipients.split(',').map(email => email.trim()).filter(email => email),
        meetingDetails: {
          date: formatDate(meetingDate),
          startTime: formatTime(meetingTime),
          endTime: endTime,
          duration: meetingDuration,
          location: meetingLocation
        }
      });

      if (response.data.message === 'Itinerary sent successfully') {
        setEmailSent(true);
        setError(null);
      } else {
        throw new Error('Failed to send email');
      }
    } catch (err) {
      setError('Failed to send email. Please try again.');
      console.error('Error sending email:', err);
    } finally {
      setIsLoading(false);
    }
  };

  // Add a function to manually calculate the end time
  const calculateEndTimeManually = () => {
    if (!meetingTime || !meetingDuration) {
      setError('Please enter both start time and duration');
      return;
    }

    try {
      // Parse the time input (format: HH:mm)
      const [hours, minutes] = meetingTime.split(':').map(Number);
      
      // Parse duration (e.g., "1 hour" or "30 minutes")
      const durationMatch = meetingDuration.match(/(\d+)\s*(hour|hours|minute|minutes)/i);
      
      if (durationMatch) {
        const durationValue = parseInt(durationMatch[1]);
        const durationUnit = durationMatch[2].toLowerCase();
        
        // Create date objects for start and end times
        const startDate = new Date();
        startDate.setHours(hours);
        startDate.setMinutes(minutes);
        
        const endDate = new Date(startDate);
        
        // Add duration to end date
        if (durationUnit.startsWith('hour')) {
          endDate.setHours(endDate.getHours() + durationValue);
        } else {
          endDate.setMinutes(endDate.getMinutes() + durationValue);
        }
        
        // Format end time in 12-hour format
        const formattedEndTime = endDate.toLocaleTimeString('en-US', {
          hour: 'numeric',
          minute: '2-digit',
          hour12: true
        });
        
        console.log('Manually calculated end time:', formattedEndTime);
        setEndTime(formattedEndTime);
        setError(null);
      } else {
        setError('Invalid duration format. Use "1 hour" or "30 minutes"');
      }
    } catch (error) {
      console.error('Error calculating end time:', error);
      setError('Error calculating end time');
    }
  };

  return (
    <div className="itinerary-manager">
      <h2>Meeting Itinerary Manager</h2>
      
      <div className="meeting-details-form">
        <h3>Meeting Details</h3>
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="meetingDate">Date:</label>
            <input
              type="date"
              id="meetingDate"
              value={meetingDate}
              onChange={(e) => setMeetingDate(e.target.value)}
              placeholder="Select date"
            />
            {meetingDate && (
              <div className="formatted-date">
                {formatDate(meetingDate)}
              </div>
            )}
          </div>
          
          <div className="form-group">
            <label htmlFor="meetingTime">Start Time:</label>
            <input
              type="time"
              id="meetingTime"
              value={meetingTime}
              onChange={(e) => setMeetingTime(e.target.value)}
              placeholder="Select time"
            />
            {meetingTime && (
              <div className="formatted-time">
                {formatTime(meetingTime)}
              </div>
            )}
          </div>
        </div>
        
        <div className="form-row">
          <div className="form-group">
            <label htmlFor="meetingDuration">Duration:</label>
            <div className="duration-input-group">
              <input
                type="text"
                id="meetingDuration"
                value={meetingDuration}
                onChange={(e) => setMeetingDuration(e.target.value)}
                placeholder="e.g., 1 hour, 30 minutes"
              />
              <button 
                type="button" 
                className="calculate-button"
                onClick={calculateEndTimeManually}
                disabled={!meetingTime || !meetingDuration}
              >
                Calculate End Time
              </button>
            </div>
            <EndTimeCalculator 
              startTime={meetingTime}
              duration={meetingDuration}
              onEndTimeChange={handleEndTimeChange}
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="meetingLocation">Location/Platform:</label>
            <input
              type="text"
              id="meetingLocation"
              value={meetingLocation}
              onChange={(e) => setMeetingLocation(e.target.value)}
              placeholder="e.g., Conference Room B, Google Meet"
            />
          </div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="itinerary-form">
        <div className="form-group">
          <label htmlFor="rawItinerary">Enter Meeting Details:</label>
          <textarea
            id="rawItinerary"
            value={rawItinerary}
            onChange={(e) => setRawItinerary(e.target.value)}
            placeholder="Enter meeting details, agenda items, or any specific requirements..."
            rows="6"
            required
          />
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={isLoading}
        >
          {isLoading ? 'Processing...' : 'Process Itinerary'}
        </button>
      </form>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {emailSent && (
        <div className="success-message">
          Email sent successfully!
        </div>
      )}

      {processedItinerary && processedItinerary.sections && (
        <div className="processed-itinerary">
          <h3>Processed Itinerary</h3>
          <div className="itinerary-content">
            {processedItinerary.sections.map((section, index) => (
              <div key={index} className="itinerary-section">
                <h4>{section.title}</h4>
                <ul>
                  {section.items.map((item, itemIndex) => (
                    <li key={itemIndex}>{item}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>

          <div className="email-form">
            <h3>Email Details</h3>
            <div className="form-group">
              <label htmlFor="recipientEmail">Recipient Email:</label>
              <input
                type="email"
                id="recipientEmail"
                value={recipientEmail}
                onChange={(e) => setRecipientEmail(e.target.value)}
                placeholder="recipient@example.com"
              />
            </div>
            <div className="form-group">
              <label htmlFor="additionalRecipients">Additional Recipients (comma-separated):</label>
              <input
                type="text"
                id="additionalRecipients"
                value={additionalRecipients}
                onChange={(e) => setAdditionalRecipients(e.target.value)}
                placeholder="cc1@example.com, cc2@example.com"
              />
            </div>
            <div className="form-group">
              <label htmlFor="subject">Subject:</label>
              <input
                type="text"
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Meeting Invitation"
              />
            </div>
            <div className="business-reference">
              <p>Business Reference: <a href="https://www.jamesperram.com.au" target="_blank" rel="noopener noreferrer">www.jamesperram.com.au</a></p>
            </div>
            <button 
              className="send-button"
              onClick={handleSendEmail}
              disabled={!recipientEmail || !subject || emailSent}
            >
              {emailSent ? 'Email Sent!' : 'Send Email'}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default ItineraryManager; 