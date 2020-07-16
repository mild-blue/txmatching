TRUNCATE TABLE public.config RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.app_user RESTART IDENTITY CASCADE;
TRUNCATE TABLE public.patient RESTART IDENTITY CASCADE;

-- Test user with password "aaa"
INSERT INTO public.app_user (id, email, pass_hash, role)
VALUES (1, 'admin@example.com', '$2b$12$3A5.4Ulau0F6AUksx9bojuYygMGNjdyPqHzrCJ1ELjqbcV28YU1Rq', 'ADMIN');