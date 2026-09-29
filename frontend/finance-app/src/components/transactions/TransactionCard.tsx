import { Box, Flex, Text } from "@chakra-ui/react";
import { type TransactionDTO } from "@/types";
import { TransactionActions } from "@/components/transactions/TransactionActions";

interface Props {
  transaction: TransactionDTO;
  onEdit(transaction: TransactionDTO): void;
  onDelete(transaction: TransactionDTO): void;
}

const TransactionCard = ({ transaction, onEdit, onDelete }: Props) => {
  return (
    <Box p={3} rounded="md" shadow="sm" bg="gray.700">
      <Flex justify="space-between" align="center">
        <Box>
          <Text>{transaction.description}</Text>
          <Text
            color={transaction.type === "income" ? "green.400" : "red.400"}
            fontWeight="bold"
          >
            {transaction.amount.toLocaleString("pt-BR", {
              style: "currency",
              currency: "BRL",
            })}
          </Text>
          <Text fontSize="xs" color="gray.500">
            {new Date(transaction.date).toLocaleDateString("pt-BR")} •{" "}
            {transaction.category.name}
          </Text>
        </Box>
        <TransactionActions
          transaction={transaction}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      </Flex>
    </Box>
  );
};

export default TransactionCard;
