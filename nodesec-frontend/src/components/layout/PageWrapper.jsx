import { motion } from 'framer-motion';

export default function PageWrapper({ children, title }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {title && <h1 className="text-2xl font-bold mb-6">{title}</h1>}
      {children}
    </motion.div>
  );
}