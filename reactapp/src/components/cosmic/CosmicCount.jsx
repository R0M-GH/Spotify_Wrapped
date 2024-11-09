import React from 'react'
import {motion} from 'framer-motion'

export default function CosmicCount() {
	const songCount = 1337

	return (
		<div className="text-center">
			<motion.h2
				className="text-3xl md:text-4xl font-bold mb-8"
				initial={{opacity: 0, y: -20}}
				animate={{opacity: 1, y: 0}}
			>
				Cosmic Conquest
			</motion.h2>
			<motion.div
				className="text-6xl md:text-8xl font-bold text-blue-400"
				initial={{scale: 0}}
				animate={{scale: 1}}
				transition={{type: "spring", stiffness: 100}}
			>
				{songCount}
			</motion.div>
			<motion.p
				className="text-xl md:text-2xl mt-4 text-blue-200"
				initial={{opacity: 0}}
				animate={{opacity: 1}}
				transition={{delay: 0.3}}
			>
				songs in your cosmic library
			</motion.p>
		</div>
	)
}