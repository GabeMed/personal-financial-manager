import { Box, Button, Heading, HStack, SimpleGrid } from "@chakra-ui/react";
import useSummary from "@/hooks/useSummary";
import useCategories from "@/hooks/useCategories";
import TransactionList from "@/components/transactions/TransactionList";
import { BalanceCard } from "@/components/layout/BalanceCard";
import { SummaryCharts } from "@/components/charts/SummaryCharts";
import { useAuth } from "@/context/AuthContext";

// Access control lives in <ProtectedRoute />.
const DashboardPage = () => {
  const { logout } = useAuth();

  const { data: summary, isLoading: summaryLoading } = useSummary();
  const { data: categories = [] } = useCategories();

  const categoryNames = Object.fromEntries(
    categories.map((c) => [String(c.id), c.name])
  );

  const expenseSlices = summary?.expense_porcentage_by_category
    ? Object.entries(summary.expense_porcentage_by_category).map(
        ([id, porcentage]) => ({
          category: categoryNames[id],
          porcentage,
        })
      )
    : [];

  const incomeSlices = summary?.income_porcentage_by_category
    ? Object.entries(summary.income_porcentage_by_category).map(
        ([id, porcentage]) => ({
          category: categoryNames[id],
          porcentage,
        })
      )
    : [];

  return (
    <Box p={6}>
      <HStack justifyContent="space-between" alignContent="center">
        <Heading size="xl" mb={6}>
          Dashboard
        </Heading>
        <Button
          marginBottom={5}
          fontWeight="bold"
          size="lg"
          variant="ghost"
          onClick={logout}
        >
          Logout
        </Button>
      </HStack>

      <SimpleGrid columns={{ base: 1, md: 2 }} gap={6} mb={8}>
        <BalanceCard
          value={summary ? summary.balance : 0}
          isLoading={summaryLoading}
        ></BalanceCard>

        <SummaryCharts expenses={expenseSlices} incomes={incomeSlices} />
      </SimpleGrid>

      <TransactionList />
    </Box>
  );
};

export default DashboardPage;
