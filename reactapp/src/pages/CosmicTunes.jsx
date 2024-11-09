import React from 'react';
import CosmicConquest from '../components/cosmic/CosmicCount';
import GenreNebula from '../components/cosmic/GenreNebula';
import StellarHits from '../components/cosmic/StellarHits';
import ArtistConstellation from '../components/cosmic/ArtistConstellation';

const CosmicTunes = () => {
	return (
		<div className="min-h-screen bg-black text-white">
			<h1 className="text-4xl font-bold text-center py-8">Cosmic Explorer</h1>
			<div className="grid grid-cols-1 md:grid-cols-2 gap-8 p-8">
				<CosmicConquest/>
				<GenreNebula/>
				<StellarHits/>
				<ArtistConstellation/>
			</div>
		</div>
	);
};

export default CosmicTunes;