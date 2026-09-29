import {
  Box,
  Button,
  Flex,
  Heading,
  Alert,
  Stack,
  Field,
  Input,
} from "@chakra-ui/react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { registerSchema, type RegisterCredentials } from "@/schemas/auth";
import { useRegister } from "@/hooks/useRegister";
import { Link, useNavigate } from "react-router-dom";

const RegistrationPage = () => {
  const navigate = useNavigate();
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterCredentials>({ resolver: zodResolver(registerSchema) });

  const { mutate: signup, isPending, error } = useRegister();

  const onSubmit = (data: RegisterCredentials) =>
    signup(data, {
      onSuccess: () => navigate("/dashboard"),
    });

  return (
    <Flex minH="100vh" align="center" justify="center">
      <Box p={8} rounded="lg" shadow="md" w="sm">
        <Heading mb={6} textAlign="center">
          Create account
        </Heading>

        {error && (
          <Alert.Root status="error" variant="solid" mb="4">
            <Alert.Indicator />
            <Alert.Title>{(error as Error).message}</Alert.Title>
          </Alert.Root>
        )}

        <form onSubmit={handleSubmit(onSubmit)}>
          <Stack gap="4">
            <Field.Root invalid={!!errors.username}>
              <Field.Label>Username</Field.Label>
              <Input placeholder="username" {...register("username")} />
              {errors.username && (
                <Field.ErrorText>{errors.username.message}</Field.ErrorText>
              )}
            </Field.Root>

            <Field.Root invalid={!!errors.email}>
              <Field.Label>Email</Field.Label>
              <Input type="email" placeholder="email" {...register("email")} />
              {errors.email && (
                <Field.ErrorText>{errors.email.message}</Field.ErrorText>
              )}
            </Field.Root>

            <Field.Root invalid={!!errors.password}>
              <Field.Label>Password</Field.Label>
              <Input type="password" {...register("password")} />
              {errors.password && (
                <Field.ErrorText>{errors.password.message}</Field.ErrorText>
              )}
            </Field.Root>

            <Button w="full" type="submit" loading={isPending}>
              Register
            </Button>
            <Box textAlign="center">
              <Link to="/">Already registered?</Link>
            </Box>
          </Stack>
        </form>
      </Box>
    </Flex>
  );
};

export default RegistrationPage;
