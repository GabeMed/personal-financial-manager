import { Alert, Dialog, Portal, Spinner, Box, Text } from "@chakra-ui/react";
import { type TransactionDTO } from "@/types";
import useAddFormTransaction from "@/hooks/useAddFormTransaction";
import useUpdateTransaction from "@/hooks/useUpdateTransaction";
import TransactionForm from "./TransactionForm";
import { type NewTransactionDTO } from "@/schemas/transaction";
import useCategories from "@/hooks/useCategories";
import { useCallback } from "react";
import { getErrorMessage } from "@/services/errors";

interface AddEditTransactionDialogProps {
  mode: "create" | "edit";
  isOpen: boolean;
  onClose(): void;
  initial?: TransactionDTO;
}

const AddEditTransactionDialog = ({
  mode,
  isOpen,
  onClose,
  initial,
}: AddEditTransactionDialogProps) => {
  const { data: categories = [], isLoading: catsLoading } = useCategories();
  const saveMutation = useAddFormTransaction();
  const updateMutation = useUpdateTransaction();

  const mutation = mode === "create" ? saveMutation : updateMutation;

  const close = useCallback(() => {
    saveMutation.reset();
    updateMutation.reset();
    onClose();
  }, [saveMutation, updateMutation, onClose]);

  const handleSubmit = useCallback(
    async (values: NewTransactionDTO) => {
      if (mode === "create") {
        await saveMutation.mutateAsync(values);
      } else if (initial) {
        await updateMutation.mutateAsync({ id: initial.id, body: values });
      }
      close();
    },
    [mode, saveMutation, updateMutation, initial, close]
  );

  const loading = catsLoading;

  return (
    <Dialog.Root
      open={isOpen}
      onOpenChange={(open) => !open && close()}
      placement="center"
      size="lg"
    >
      <Portal>
        <Dialog.Backdrop />
        <Dialog.Positioner>
          <Dialog.Content>
            <Dialog.Header>
              <Dialog.Title>
                {mode === "create" ? "New transaction" : "Edit transaction"}
              </Dialog.Title>
            </Dialog.Header>

            <Dialog.Body>
              {mutation.error && (
                <Alert.Root status="error" mb="4">
                  <Alert.Indicator />
                  <Alert.Title>{getErrorMessage(mutation.error)}</Alert.Title>
                </Alert.Root>
              )}
              {loading ? (
                <Box py={6} textAlign="center">
                  <Spinner />
                  <Text mt={2} color="gray.400">
                    Loading ...
                  </Text>
                </Box>
              ) : (
                <TransactionForm
                  categories={categories}
                  initial={initial}
                  onSubmit={handleSubmit}
                  onCancel={close}
                />
              )}
            </Dialog.Body>
          </Dialog.Content>
        </Dialog.Positioner>
      </Portal>
    </Dialog.Root>
  );
};

export default AddEditTransactionDialog;
