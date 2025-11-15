import React from 'react';
import { useParams } from 'react-router-dom';
import ScanDetails from '../components/ScanDetails/ScanDetails';

const ScanDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  return <ScanDetails scanId={id || ''} />;
};

export default ScanDetailsPage;