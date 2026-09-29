import { Box, Text } from "@chakra-ui/react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

interface Slice {
  category: string;
  porcentage: number;
}

interface PieChartCardProps {
  title: string;
  data: Slice[];
}

const COLORS = ["#38B2AC", "#ED8936", "#63B3ED", "#E53E3E", "#718096"];

const PieChartCard = ({ title, data }: PieChartCardProps) => {
  if (data.length === 0) {
    return (
      <Box bg="gray.700" p={6} rounded="2xl" shadow="lg" textAlign="center">
        <Text fontSize="sm" color="gray.400">
          No {title.toLowerCase()} registered
        </Text>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Text mb={2} fontWeight="bold">
        {title}
      </Text>
      <ResponsiveContainer width="100%" height={260}>
        <PieChart>
          <Pie
            data={data}
            dataKey="porcentage"
            nameKey="category"
            cx="50%"
            cy="50%"
            outerRadius={80}
          >
            {data.map((_, idx) => (
              <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip formatter={(val: number) => `${val.toFixed(1)}%`} />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default PieChartCard;
