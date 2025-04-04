import React from 'react';
import ItineraryManager from './components/ItineraryManager';

function App() {
  const handleItineraryUpdate = (processedItinerary) => {
    console.log('Processed itinerary:', processedItinerary);
  };

  return (
    <div className="app">
      <ItineraryManager onItineraryUpdate={handleItineraryUpdate} />
    </div>
  );
}

export default App; 